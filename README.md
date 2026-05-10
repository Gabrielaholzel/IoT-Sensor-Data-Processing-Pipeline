# IoT Sensor Data Processing Pipeline

A serverless pipeline for ingesting, processing, and storing real-time IoT sensor data using AWS.

## Architecture Overview

The pipeline is fully serverless, built on four AWS services:

1. **Amazon Kinesis** — streams live IoT data into the pipeline in real time
2. **AWS Lambda** — processes incoming data in batches of 50 records
3. **Amazon Redshift** — stores structured sensor data for querying and analytics
4. **Amazon S3** — stores sensor data in Parquet format for cost-effective long-term storage

![Architecture](Sensor-Based%20Architecture.jpeg)

## Technologies Used

| Tool | Purpose |
|---|---|
| AWS Lambda | Serverless batch processing |
| Amazon Kinesis | Real-time data streaming |
| Amazon Redshift | Data warehouse |
| Amazon S3 | Long-term Parquet storage |
| AWS Data Wrangler | Data manipulation with Pandas-like syntax |
| Pandas | Batch data processing |
| Boto3 | Python SDK for AWS |

## How It Works

1. IoT sensor data is ingested via **Kinesis** in real time
2. **Lambda** processes records in batches of 50, optimising throughput
3. Processed data is written to **Redshift** for analytics and to **S3** in Parquet format for long-term storage
4. Redshift supports complex queries for trend analysis and reporting

## Setup

### Prerequisites

- AWS account with permissions for Lambda, Kinesis, Redshift, and S3
- Python 3.9

### Environment Variables

Set the following on the Lambda function:

```
REDSHIFT_CLUSTER_ID
REDSHIFT_DATABASE
REDSHIFT_USER
BUCKET
KEY
```

### Dependencies

Package the following libraries as a Lambda Layer or via SAM:

```
awswrangler
pandas
boto3
```

### AWS Resources

- Create an **S3 bucket** for Parquet output
- Create a **Redshift cluster** with the appropriate schema for sensor data
- Configure **Kinesis** stream and attach it as a Lambda trigger
