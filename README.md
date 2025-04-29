# Project: Data Pipelines with Airflow
A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.

They have decided to bring you into the project and expect you to create high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

![Example DAG](/assets/2025-04-28%2020_31_38-Data%20Pipelines%20-%20Project%20Overview.png)

## Project Prerequisites

An AWS IAM User with the following permissions
* AdminstratorAccess
* AmazonRedshiftFullAccess
* AmazonS3FullAccess

Populate the [dwh.cfg](/dwh.cfg) file with the IAM User's KEY and SECRET

![AWS Keys and Secret in dwh.cfg](/assets/2025-04-29%2000_00_30-dwh.cfg%20-%20secrets%20and%20keys.png)

## Project Datasets

The following source datasets are used:

1. s3://udacity-dend/log_data
    - **NOTE** include also the JSON metadata for this: s3://udacity-dend/log_json_path.json 
2. s3://udacity-dend/song-data

## Initiating the Airflow Web Server
Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed before proceeding.

To bring up the entire app stack up, we use [docker-compose](https://docs.docker.com/engine/reference/commandline/compose_up/) as shown below

```bash
docker-compose up -d
```
Create admin credentials for the Airflow Web Server run the following command

```bash
docker-compose run airflow-worker airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
```

Then go to http://localhost:8080/ - this is default port for Airflow on a local machine

### Add AWS Credentials to Airflow

The same key and secret placed in [dwh.cfg](/dwh.cfg) will also need to be placed in Airflow.

Go to the Airflow UI --> Admin --> Connections --> Add New Record (little blue plus sign)

Connection Type = "Amazon Web Services"

![Airflow Add AWS Credentials](/assets/2025-04-29%2000_14_16-Add%20AWS%20Connection%20-%20Airflow.png)

## Deploying AWS Infrastructure with IaC

Run the [infra_deploy.py](/infra_deploy.py) to set up the following using boto3:
1. Create a target S3 Bucket
2. Copy datasets from source S3 to target S3
3. Create the IAM Role for Redshift service
4. Attach S3 full access policy to S3 role
5. Create the Redshift cluster
6. Configure VPC ingress rules
7. Output the Cluster endpoint and IAM Role ARN

### Add HOST and ARN Variables to dwh.cfg

Add to HOST and ARN variable to [dwh.cfg](/dwh.cfg)

![dwh.cfg with Host and Arn](/assets/2025-04-29%2000_00_30-dwh.cfg%20-%20udacity-nd-data-engineering-aws-project-airflow-data-pipelines%20-%20Visua.png)

### Add Redshift Connection to Airflow

With the HOST known, go to Airflow UI --> Admin --> Connections --> Add New Record

Connection Type = "Amazon Redshift"

Use the CLUSTER variables in [dwh.cfg](/dwh.cfg) to fill out the rest

![Airflow with HOST](/assets/2025-04-29%2000_05_33-Add%20Redshift%20Connection%20-%20Airflow.png)

## Copy S3 Data to Target Bucket

In the AWS CLI run the following commands

First copy S3 source data to home cloudshell directory

```bash
aws s3 cp s3://udacity-dend/log-data/ ~/log-data/ --recursive
aws s3 cp s3://udacity-dend/song-data/ ~/song-data/ --recursive
aws s3 cp s3://udacity-dend/log_json_path.json ~/
```

Then copy from home cloudshell directory to the target S3 bucket

```bash
aws s3 cp ~/log-data/ s3://udacity-dend-ba-copy/log-data/ --recursive
aws s3 cp ~/song-data/ s3://udacity-dend-ba-copy/song-data/ --recursive
aws s3 cp ~/log_json_path.json s3://udacity-dend-ba-copy/
```

## NEXT TO DO