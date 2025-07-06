import boto3
import logging
from botocore.exceptions import NoCredentialsError
import os

def upload_folder_to_s3(local_folder, bucket_name, s3_prefix):
    s3 = boto3.client("s3")

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.join(s3_prefix, os.path.relpath(local_path, local_folder))
            print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}")
            s3.upload_file(local_path, bucket_name, s3_key)
            
def upload_file_to_s3(local_path, bucket_name, s3_key):
    s3 = boto3.client("s3")
    try:
        s3.upload_file(local_path, bucket_name, s3_key)
        logging.info(f"S3-UPLOAD: Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
    except NoCredentialsError:
        logging.error("S3-UPLOAD-ERROR: AWS credentials not found")