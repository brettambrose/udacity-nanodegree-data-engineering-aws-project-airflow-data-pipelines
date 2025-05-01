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

1. Go to the [deploy](/deploy/) folder
2. run the [infra_deploy.py](/deploy/infra_deploy.py) script, which will use boto3 to...
    1. Create the IAM Role for Redshift service
    2. Attach S3 full access policy to S3 role
    3. Create the Redshift cluster
    4. Configure VPC ingress rules
    5. Output the Cluster endpoint and IAM Role ARN for use in th [Add HOST and ARN Variables to dwh.cfg](#add-host-and-arn-variables-to-dwhcfg) and [Add Redshift Connection to Airflow](#add-redshift-connection-to-airflow) steps
3. run the [create_tables.py](/deploy/create_tables.py) script, which will create all tables in the DWH using the SQL statements in [ddl.py](/deploy/ddl.py)

### Add HOST variable to dwh.cfg

Add to HOST variable to [dwh.cfg](/dwh.cfg)

![dwh.cfg with Host](/assets/2025-04-30%2021_00_09-dwh.cfg%20-%20HOST%20variable.png)

### Add Redshift Connection to Airflow

With the HOST known, go to Airflow UI --> Admin --> Connections --> Add New Record

Connection Type = "Amazon Redshift"

Use the CLUSTER variables in [dwh.cfg](/dwh.cfg) to fill out the rest

![Airflow with HOST](/assets/2025-04-29%2000_05_33-Add%20Redshift%20Connection%20-%20Airflow.png)

### Run the DAG in Airflow

Now all the connections are set up, run the [sparkify_etl](/dags/sparkify_etl.py) DAG in airflow.  The DAG should look like this:

![Sparkify ETL DAG](/assets/2025-04-30%2021_04_07-Airflow%20DAG.png)