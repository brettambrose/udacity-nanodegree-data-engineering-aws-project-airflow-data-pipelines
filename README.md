# Project: Data Pipelines with Airflow

# Contents
1. [Project Summary](#project-summary)
2. [Project Prerequisites](#project-prerequisites)
    1. [AWS Account with IAM User](#aws-account-with-iam-user)
    2. [Docker Desktop](#docker-desktop)
3. [Project Datasets](#project-datasets)
4. [Initiating the Airflow Web Server](#initiating-the-airflow-web-server)
    1. [Add AWS Credentials to Airflow](#add-aws-credentials-to-airflow)
5. [Deploying AWS Infrastructure with IaC](#deploying-aws-infrastructure-with-iac)
    1. [Add HOST variable to dwh.cfg](#add-host-variable-to-dwhcfg)
    2. [Add Redshift Connection to Airflow](#add-redshift-connection-to-airflow)
6. [Running the DAG in Airflow](#running-the-dag-in-airflow)
7. [Decommissioning Docker and Redshift](#decommissioning-docker-and-redshift)

## Project Summary
A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.

They have decided to bring you into the project and expect you to create high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

![Example DAG](/assets/2025-04-28%2020_31_38-Data%20Pipelines%20-%20Project%20Overview.png)

## Project Prerequisites

### AWS Account with IAM User
An AWS IAM User with the following permissions
* AdminstratorAccess
* AmazonRedshiftFullAccess
* AmazonS3FullAccess

Populate the [dwh.cfg](/dwh.cfg) file with the IAM User's KEY and SECRET

![AWS Keys and Secret in dwh.cfg](/assets/2025-04-29%2000_00_30-dwh.cfg%20-%20secrets%20and%20keys.png)

### Docker Desktop and Apache Airflow

This project uses Apache Airflow 2.5.1.  For more documentation on Apache Airflow go to https://airflow.apache.org/docs/apache-airflow/2.5.1/

1. Download docker from https://www.docker.com/products/docker-desktop/
2. The [docker-compose.yml](/docker-compose.yml) file is in this repo, but can be downloaded if needed here:https://airflow.apache.org/docs/apache-airflow/2.5.1/docker-compose.yaml
3. Ensure a **.env** file is in a local copy of this repo, populated with the following:

<pre>
AIRFLOW_IMAGE_NAME=apache/airflow:2.5.1
AIRFLOW_UID=50000
</pre>

## Project Datasets

The following source datasets are used:

> s3://udacity-dend/log-data
>
>s3://udacity-dend/song_data

**NOTE** a JSON path metadata file needs to be used for /log-data

> s3://udacity-dend/log_json_path.json 

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

Then go to http://localhost:8080/ - this is default port for Airflow on a local machine and log in using the credentials created above

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

## Running the DAG in Airflow

Now all the connections are set up, run the [sparkify_etl](/dags/sparkify_etl.py) DAG in airflow. 

Go to in https://localhost:8080/ --> DAGS --> scroll down to sparkify_etl DAG

![Airflow DAG page](/assets/2025-05-01%2007_43_10-DAGs%20-%20Airflow.png)

Run the DAG by selecting the RUN botton at the top right.  Review the DAG by going to "Graph" to track the execution visually.

![Sparkify ETL DAG](/assets/2025-05-01%2007_47_18-sparkify_etl%20-%20Sparkify%20ETL%20DAG%20Graph.png)

Verify DAG Success by hovering over and clicking on tasks...

![DAG Success](/assets/2025-05-01%2008_13_29-sparkify_etl%20-%20DAG%20Success.png)

... and reviewing task logs
![Task Log](/assets/2025-05-01%2008_15_12-sparkify_etl%20-%20Task%20Logs.png)

## Decommissioning Docker and Redshift

Once the ETL DAG runs successfully, execute the following terminal command to shutdown the docker container:
```bash
docker-compose down
```

Then run the [infra_decomm.py](/deploy/infra_decomm.py) scrip in the [deploy](/deploy/) folder to:
1. Delete the Redshift Cluster
2. Delete the IAM Role