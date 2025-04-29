import boto3
import configparser

config = configparser.ConfigParser()
config.read('dwh.cfg')

#AWS
KEY = config.get("AWS","KEY")
SECRET = config.get("AWS","SECRET")

# IAM
IAM_ROLE_NAME = config.get("IAM_ROLE","IAM_ROLE_NAME")

# CLUSTER CONFIGURATIONS
CLUSTER_IDENTIFIER = config.get("INFRASTRUCTURE","CLUSTER_IDENTIFIER")

# S3
S3_TGT_BUCKET_NAME = config.get("S3","S3_TGT_BUCKET_NAME")

print("*******************************************")
print("Establishing boto3 iam, s3, and redshift clients")

iam = boto3.client('iam',aws_access_key_id=KEY,
                     aws_secret_access_key=SECRET,
                     region_name='us-east-1'
                  )

s3 = boto3.resource("s3",
                    region_name="us-east-1",
                    aws_access_key_id=KEY,
                    aws_secret_access_key=SECRET
                   )

s3_client = boto3.client("s3",
                         region_name="us-east-1",
                         aws_access_key_id=KEY,
                         aws_secret_access_key=SECRET
                        )

redshift = boto3.client('redshift',
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET,
                       region_name="us-east-1"
                       )

print("*************************************")
print("Deleting S3 Bucket and Its Objects...")

try:
    s3_object_resp = s3.Bucket(S3_TGT_BUCKET_NAME).objects.all().delete()
except Exception as e:
    print(e)

try:
    s3_bucket_resp = s3_client.delete_bucket(Bucket=S3_TGT_BUCKET_NAME)
except Exception as e:
    print(e)


print("*******************")
print("Deleting Cluster...")

redshift.delete_cluster( ClusterIdentifier=CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)

print(redshift.describe_clusters(ClusterIdentifier=CLUSTER_IDENTIFIER)['Clusters'][0])

print("*******************************")
print("Detatching IAM Role policies...")

iam.detach_role_policy(RoleName=IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")

print("*****************")
print("Deleting IAM Role")

iam.delete_role(RoleName=IAM_ROLE_NAME)