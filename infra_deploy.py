import boto3
import json
import psycopg2
import configparser

config = configparser.ConfigParser()
config.read('dwh.cfg')

# AWS CREDENTIALS
KEY                = config.get("AWS","KEY")
SECRET             = config.get("AWS","SECRET")

# IAM ROLES
IAM_ROLE_NAME      = config.get("IAM_ROLE","IAM_ROLE_NAME")

# CLUSTER CONFIGURATIONS
CLUSTER_IDENTIFIER = config.get("INFRASTRUCTURE","CLUSTER_IDENTIFIER")
CLUSTER_TYPE       = config.get("INFRASTRUCTURE","CLUSTER_TYPE")
NODE_TYPE          = config.get("INFRASTRUCTURE","NODE_TYPE")
NUM_NODES          = config.get("INFRASTRUCTURE","NUM_NODES")

# DATABASE CONFIGURATIONS
DB_NAME            = config.get("CLUSTER","DB_NAME")
DB_USER            = config.get("CLUSTER","DB_USER")
DB_PASSWORD        = config.get("CLUSTER","DB_PASSWORD")
DB_PORT            = config.get("CLUSTER","DB_PORT")

# S3 Bucket
S3_SRC_BUCKET_NAME = config.get("S3","S3_SRC_BUCKET_NAME")
S3_TGT_BUCKET_NAME = config.get("S3","S3_TGT_BUCKET_NAME")

print("*******************************************************************")
print("Establishing boto3 resources and clients")

iam = boto3.client('iam',aws_access_key_id=KEY,
                     aws_secret_access_key=SECRET,
                     region_name='us-east-1'
                  )

redshift = boto3.client('redshift',
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET,
                       region_name="us-east-1"
                       )

ec2 = boto3.resource('ec2',
                     aws_access_key_id=KEY,
                     aws_secret_access_key=SECRET,
                     region_name='us-east-1'
                     )


s3_client = boto3.client("s3",
                         region_name="us-east-1",
                         aws_access_key_id=KEY,
                         aws_secret_access_key=SECRET
                         )

print("*********************")
print("Creating S3 bucket...")

try:
    s3_client.create_bucket(
        Bucket=S3_TGT_BUCKET_NAME
    )

except Exception as e:
    print(e)


print("**********************************************************")
print("Creating IAM Role with permissions to use Redshift service")

try:
    dwhRole = iam.create_role(
        Path='/',
        RoleName=IAM_ROLE_NAME,
        Description = "Allows Redshift clusters to call AWS services on your behalf.",
        AssumeRolePolicyDocument=json.dumps(
            {'Statement': [{'Action': 'sts:AssumeRole',
               'Effect': 'Allow',
               'Principal': {'Service': 'redshift.amazonaws.com'}}],
             'Version': '2012-10-17'})
    )    
except Exception as e:
    print(e)

print("************************************************")
print("Attaching S3 Full Access policy to IAM Role")

iam.attach_role_policy(RoleName=IAM_ROLE_NAME,
                       PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
                      )['ResponseMetadata']['HTTPStatusCode']

ARN = iam.get_role(RoleName=IAM_ROLE_NAME)['Role']['Arn']

print("***********************************")
print('Creating cluster...')

try:
    response = redshift.create_cluster(        
        #HW
        ClusterType=CLUSTER_TYPE,
        NodeType=NODE_TYPE,
        NumberOfNodes=int(NUM_NODES),

        #Identifiers & Credentials
        DBName=DB_NAME,
        ClusterIdentifier=CLUSTER_IDENTIFIER,
        MasterUsername=DB_USER,
        MasterUserPassword=DB_PASSWORD,
        PubliclyAccessible=True,
        
        #Roles (for s3 access)
        IamRoles=[ARN]
    )
except Exception as e:
    print(e)

while redshift.describe_clusters(ClusterIdentifier=CLUSTER_IDENTIFIER)['Clusters'][0]['ClusterStatus'] != 'available':
    False
else:

    print("Cluster created!")
    print('Waiting for cluster availability...')
    
    while redshift.describe_clusters(ClusterIdentifier=CLUSTER_IDENTIFIER)['Clusters'][0]['ClusterAvailabilityStatus'] != 'Available':
        False
    else:
        print('Cluster available!')

myClusterProps = redshift.describe_clusters(ClusterIdentifier=CLUSTER_IDENTIFIER)['Clusters'][0]



print("Confliguring VPC Inbound Rules...")

try:
    vpc = ec2.Vpc(id=myClusterProps['VpcId'])
    defaultSg = list(vpc.security_groups.all())[0]
    print(defaultSg)
    defaultSg.authorize_ingress(
        GroupName=defaultSg.group_name,
        CidrIp='0.0.0.0/0',
        IpProtocol='TCP',
        FromPort=0,
        ToPort=5500
        # FromPort=int(DWH_PORT),
        # ToPort=int(DWH_PORT)
    )
except Exception as e:
    print(e)

print("**********************************")
print("Validation AWS Redshift connection")

HOST = myClusterProps['Endpoint']['Address']

conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT))
conn.close()

print('Connected to Redshift!')

print("*************************************************************")
print("Use the following for HOST and ARN variables in DWH Config:\n")
print("*************************************************************")

print("[CLUSTER]")
print("HOST=" + HOST + "\n")
print("[IAM_ROLE]")
print("ARN=" + ARN)