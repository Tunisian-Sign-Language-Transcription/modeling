import boto3
import botocore

BUCKET_NAME = 'ieee-dataport' 

s3 = boto3.resource('s3')
keys = []

txt_file = open("s3-uris.txt", "r")

keys = txt_file.readlines()


for key in keys:
    try:
        s3.Bucket(BUCKET_NAME).download_file(key, 'test.svo')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise