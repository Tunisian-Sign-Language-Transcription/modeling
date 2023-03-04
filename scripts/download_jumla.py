import boto3
import botocore
import os
import settings as s

BUCKET_NAME = 'ieee-dataport' 

s3 = boto3.resource('s3')
keys = []

txt_file = open("s3-uris.txt", "r")


### HERE
begin = 12
end = 24
###



keys = txt_file.readlines()

total = len(keys)

keys = keys[begin:end]


index = begin


for key in keys:
    try:
        output = f'{key.split("/")[-3]}_{key.split("/")[-2]}_{key.split("/")[-1].split(".")[-2]}.{keys[0].split(".")[-1]}'
        index +=1
        print(f'Downloading ({index}/{total}): {output}')
        output_path = os.path.join(s.DATA_DIR,"jumla","svo",output)
        s3.Bucket(BUCKET_NAME).download_file(key[19:].strip(), output_path.strip())
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise