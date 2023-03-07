import boto3
import botocore
import os
import settings as s
import re
import pandas as pd
import shutil
import abc
import argparse

args = abc.abstractproperty()

BUCKET_NAME = 'ieee-dataport'

s3 = boto3.resource('s3')


def download_vids():
    keys = []
    txt_file = open("./resources/s3-uris.txt", "r")
    f = open("./resources/index.txt", "r")
    index = int(f.read())

    # CHOOSE YOUR RANGE HERE
    end = 806
    ###
    keys = txt_file.readlines()
    total = 806

    filtered_keys = [key.strip()
                     for key in keys if 'rec0' in key.strip()][index:end]

    for key in filtered_keys:
        try:
            video = {}
            video['participant'] = key.split('/')[-3]
            video['sign_code'] = re.findall(r'\d+', key.split('/')[-2])[0]

            sign_dir_path = os.path.join(
                s.DATA_DIR, 'jumla', 'raw', video['sign_code'])
            video_output_path = os.path.join(
                sign_dir_path, f'{video["participant"]}.svo')

            if os.path.exists(sign_dir_path):
                with open('./resources/index.txt', 'w') as f:
                    f.write(str(index))
                print(
                    f'Downloading ({index}/{total}): Sign: {video["sign_code"]} :Participant: {video["participant"]}')
                s3.Bucket(BUCKET_NAME).download_file(
                    key[19:].strip(), video_output_path)
                index += 1
            else:
                os.mkdir(sign_dir_path)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


def map_code_sign():
    sign_df = pd.read_excel('./resources/sign_index.xlsx')[['CODE', 'INTENT_ARABIC']]
    sign_dict = sign_df.set_index('CODE').to_dict()['INTENT_ARABIC']

    for key in sign_dict:
        sign_code = f'0{str(key)}' if len(str(key)) == 2 else str(key) # Add back leading 0
        sign_intent = sign_dict[key]
        
        dst_path = os.path.join(s.DATA_DIR,"jumla","raw",sign_intent)
        src_path = os.path.join(s.DATA_DIR,"jumla","raw",sign_code)

        if os.path.exists(dst_path) == False and os.path.exists(src_path) == True:
            
            print(f'{src_path} -> {dst_path}')
            os.rename(src_path, dst_path)
        elif os.path.exists(dst_path) == True and os.path.exists(src_path) == False:
            print(f'{sign_intent} already exists.')



def move_duplicates():
    sign_df = pd.read_excel('./resources/sign_index.xlsx')[['CODE', 'INTENT_ARABIC']]
    sign_dict = sign_df.set_index('CODE').to_dict()['INTENT_ARABIC']
    codes = sign_df['CODE'].unique() 
    subdirectories = os.listdir(os.path.join(s.DATA_DIR,'jumla','raw'))
    for subdirectory in subdirectories:
        if subdirectory.isnumeric():
            dst_path = os.path.join(s.DATA_DIR,"jumla","raw",sign_dict[int(subdirectory)])
            src_path = os.path.join(s.DATA_DIR,"jumla","raw",subdirectory)

            if os.path.exists(dst_path):
                src_files = os.listdir(src_path)
                for src_file in src_files: 
                    src_file_path = os.path.join(src_path,src_file)
                    print(f'Moving: {src_file} -> {dst_path}')
                    shutil.copy(src_file_path,dst_path)

def remove_duplicates():
    jumla_raw_path = os.path.join(s.DATA_DIR,'jumla','raw') 
    subdirectories = os.listdir(jumla_raw_path)
    for sub in subdirectories:
        if sub.isnumeric():
            shutil.rmtree(os.path.join(jumla_raw_path,sub))
            



def parse_args():
    parser = argparse.ArgumentParser(
        description='Download Jumla Dataset')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--map', action='store_true')
    parser.add_argument('--move-duplicates', action='store_true')
    parser.add_argument('--remove-duplicates', action='store_true')
 
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    global_args = parse_args()
    args.download = global_args.download
    args.map = global_args.map
    args.move_duplicates = global_args.move_duplicates
    args.remove_duplicates = global_args.remove_duplicates
    
    if args.map == True:
        map_code_sign()
    elif args.download == True:
        download_vids()
    elif args.move_duplicates == True:
        move_duplicates()
    elif args.remove_duplicates == True:
        remove_duplicates()
