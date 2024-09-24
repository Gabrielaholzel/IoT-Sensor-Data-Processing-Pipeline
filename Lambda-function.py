# Libraries
import boto3
import json
import time
from base64 import b64decode
import pandas as pd
import awswrangler as wr
import os


# Environment variables
redshift_cluster_id = os.getenv('REDSHIFT_CLUSTER_ID')
redshift_database = os.getenv('REDSHIFT_DATABASE')
redshift_user = os.getenv('REDSHIFT_USER')
bucket = os.getenv('BUCKET')
key = os.getenv('KEY')
batch_size = os.getenv('BATCH_SIZE')


def get_redshift_connection(redshift_cluster_id=redshift_cluster_id, 
                            redshift_database=redshift_database, 
                            redshift_user=redshift_user):
    """
    Establish a connection to Amazon Redshift using the redshift-data client.
    
    Parameters:
    - redshift_cluster_id (str): The Redshift cluster identifier.
    - redshift_database (str): The database name in the Redshift cluster.
    - redshift_user (str): The Redshift user with access to the database.
    
    Returns:
    - client: A boto3 client object for interacting with Redshift if successful.
    - None: Returns None if there is an error establishing the connection.
    """
    try:
        client = boto3.client('redshift-data')
        return client
    except Exception as e:
        print(f"Error connecting to Redshift: {e}")
        return None


def execute_query(query, redshift_cluster_id=redshift_cluster_id, 
                  redshift_database=redshift_database, 
                  redshift_user=redshift_user):
    """
    Executes an SQL query on the specified Redshift database.
    
    Parameters:
    - query (str): The SQL query to execute.
    - redshift_cluster_id (str): The Redshift cluster identifier.
    - redshift_database (str): The database name in the Redshift cluster.
    - redshift_user (str): The Redshift user with access to the database.
    
    Returns:
    - dict: Returns a success message if the query is executed successfully.
    - dict: Returns an error message if the query fails to execute.
    """
    client = get_redshift_connection()

    if client is None:
        return {
            'statusCode': 500,
            'body': 'Could not establish connection to Redshift.'
        }

    try:
        response = client.execute_statement(
            ClusterIdentifier=redshift_cluster_id,
            Database=redshift_database,
            DbUser=redshift_user,
            Sql=query
        )
        print("Query executed successfully")
    except Exception as e:
        print(f"Error executing query: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }


def write_into_s3(df, bucket=bucket, key=key):
    """
    Writes a pandas DataFrame into an S3 bucket in Parquet format.
    
    Parameters:
    - df (pandas.DataFrame): The DataFrame to be saved.
    - bucket (str): The S3 bucket name where the file will be saved.
    - key (str): The S3 object key (file path) within the bucket.
    
    Returns:
    - dict: Returns a success message if the file is written successfully.
    - dict: Returns an error message if the file write operation fails.
    """
    s3 = boto3.client('s3')
    
    # Add timestamp to the file name
    key += f'-{time.strftime("%H%M%S")}.parquet'
    path = f's3://{bucket}/{key}'
    
    try:
        wr.s3.to_parquet(df, path=path)
        print(f"Data successfully written to S3 at {path}")
    except Exception as e:
        print(f"Error writing to S3: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }


def lambda_handler(event, context):
    """
    AWS Lambda function to process records in batches from a Kinesis stream, 
    insert them into an Amazon Redshift database, 
    and write the records into an S3 bucket as a Parquet file.

    Parameters:
    - event (dict): Event data passed by Kinesis stream containing records.
    - context (LambdaContext): Runtime information of the Lambda function.

    Returns:
    - dict: A response indicating success or failure.
    """
    # Get connection to Redshift
    client = get_redshift_connection()
    
    if client is None:
        return {
            'statusCode': 500,
            'body': 'Could not establish connection to Redshift.'
        }

    # Initialize an empty list for batching records and a DataFrame for S3
    batch = []
    df = pd.DataFrame()

    # Iterate through the records from the Kinesis stream
    for i in range(len(event['Records'])):
        # Kinesis data is base64 encoded, so decode it
        payload = json.loads(b64decode(event['Records'][i]['kinesis']['data']).decode('utf-8'))
        
        # Add the decoded payload to the batch list
        batch.append(payload)
        
        # Append the payload to a pandas DataFrame for S3 storage
        df = pd.concat([df, pd.DataFrame([payload])], ignore_index=True)

        # Process the batch when the batch size is reached
        if len(batch) >= batch_size:
            # Prepare the SQL query for batch insertion into Redshift
            values = ', '.join([f"({b['sensor_id']}, {b['temperature']}, {b['humidity']}, {b['timestamp']})" for b in batch])
            query = f"INSERT INTO sensors (sensor_id, temperature, humidity, timestamp) VALUES {values}"
            execute_query(query)
            
            # Clear the batch after processing
            batch.clear()

    # Process any remaining records in the batch that did not reach the batch size
    if batch:
        values = ', '.join([f"({b['sensor_id']}, {b['temperature']}, {b['humidity']}, {b['timestamp']})" for b in batch])
        query = f"INSERT INTO sensors (sensor_id, temperature, humidity, timestamp) VALUES {values}"
        execute_query(query)

    # Write the accumulated DataFrame to S3 as a Parquet file after all records have been processed
    if not df.empty:
        write_into_s3(df)

    # Return a success response
    return {
        'statusCode': 200,
        'body': 'Execution successful'
    }
