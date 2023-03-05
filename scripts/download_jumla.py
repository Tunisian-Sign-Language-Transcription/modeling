import boto3
import botocore
import os
import settings as s
import re

BUCKET_NAME = 'ieee-dataport' 

s3 = boto3.resource('s3')
keys = []

txt_file = open("s3-uris.txt", "r")



f = open("index.txt", "r")

index = int(f.read()) -1

### CHOOSE YOUR RANGE HERE
end = 1000
###
keys = txt_file.readlines()
total = end - index
filtered_keys = [key.strip() for key in keys if 'rec0' in key.strip()][index:end]


for key in filtered_keys:
    try:
        video = {}
        video['participant'] = key.split('/')[-3]
        video['sign_code'] = re.findall(r'\d+',key.split('/')[-2])[0]


        sign_dir_path = os.path.join(s.DATA_DIR,'jumla','raw',video['sign_code']) 
        video_output_path = os.path.join(sign_dir_path,f'{video["participant"]}.svo')

        if os.path.exists(sign_dir_path):
            index+=1
            with open('index.txt', 'w') as f:
                f.write(str(index))
            print(f'Downloading ({index}/{total}): Sign: {video["sign_code"]} :Participant: {video["participant"]}')
            s3.Bucket(BUCKET_NAME).download_file(key[19:].strip(), video_output_path)
        else:
            os.mkdir(sign_dir_path)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise