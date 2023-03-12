import boto3
import botocore
import os
import settings as s
import re
import pandas as pd
import shutil
import abc
import argparse
from svo_export import convert

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
    sign_df = pd.read_excel(
        './resources/sign_index.xlsx')[['CODE', 'INTENT_ARABIC']]
    sign_dict = sign_df.set_index('CODE').to_dict()['INTENT_ARABIC']

    for key in sign_dict:
        #sign_code = f'0{str(key)}' if len(
        #    str(key)) == 2 else str(key)  # Add back leading 0
        sign_code =str(key)
        sign_intent = sign_dict[key]

        dst_path = os.path.join(s.DATA_DIR, "jumla", "combined", sign_intent)
        src_path = os.path.join(s.DATA_DIR, "jumla", "combined", sign_code)

        if os.path.exists(dst_path) == False and os.path.exists(src_path) == True:
            print(f'{src_path} -> {dst_path}')
            os.rename(src_path, dst_path)
        elif os.path.exists(dst_path) == True and os.path.exists(src_path) == False:
            print(f'{sign_intent} already exists.')
            


def move_duplicates():
    sign_df = pd.read_excel(
        './resources/sign_index.xlsx')[['CODE', 'INTENT_ARABIC']]
    sign_dict = sign_df.set_index('CODE').to_dict()['INTENT_ARABIC']
    codes = sign_df['CODE'].unique()
    subdirectories = os.listdir(os.path.join(s.DATA_DIR, 'jumla', 'combined'))

   
   
    for subdirectory in subdirectories:
        if subdirectory.isnumeric():
            dst_path = os.path.join(
                s.DATA_DIR, "jumla", "combined", sign_dict[int(subdirectory)])
            src_path = os.path.join(s.DATA_DIR, "jumla", "combined", subdirectory)

            if os.path.exists(dst_path):
                src_files = os.listdir(src_path)
                for src_file in src_files:
                    src_file_path = os.path.join(src_path, f'{src_file}')
                    new_src_file_path = os.path.join(s.DATA_DIR,"jumla","combined",subdirectory,f'{src_file.replace(".svo","")}_{subdirectory}.svo')
                   
                    os.rename(src_file_path,new_src_file_path)
                    print(f'Moving: {src_file} -> {dst_path}')
                    shutil.copy(new_src_file_path, dst_path)


def remove_duplicates():
    jumla_raw_path = os.path.join(s.DATA_DIR, 'jumla', 'combined')
    subdirectories = os.listdir(jumla_raw_path)
    for sub in subdirectories:
        if sub.isnumeric():
            shutil.rmtree(os.path.join(jumla_raw_path, sub))


def create_combined_folder():
    combined_path = os.path.join(s.DATA_DIR, "jumla", "combined")
    codes = pd.read_excel('./resources/sign_index.xlsx')['CODE'].tolist()
    for code in codes:
        os.makedirs(os.path.join(combined_path, str(code)))


def add_leading_zero(codes):
    modified = []
    for code in codes:
        code = f'0{code}' if len(code) == 2 else code
        modified.append(code)

    return modified


def add_to_combined(combined_codes,name_codes, directory):
    for combined_code in combined_codes:
        for name_code in name_codes:
            if int(name_code) == int(combined_code):                
                videos = os.listdir(os.path.join(s.DATA_DIR,"jumla",directory,name_code))
                for video in videos:
                    src_file_path = os.path.join(s.DATA_DIR,"jumla",directory,name_code,video)
                    dst_file_path = os.path.join(s.DATA_DIR,"jumla","combined",combined_code)
                    if os.path.exists(os.path.join(dst_file_path,video)) == False:
                        print(f'Copying {video} from {directory}\n')
                        shutil.copy(src_file_path, dst_file_path)


def combine_dataset():
    combined_path = os.path.join(s.DATA_DIR, "jumla", "combined")
    dhia_path = os.path.join(s.DATA_DIR, "jumla", "dhia")
    rima_path = os.path.join(s.DATA_DIR, "jumla", "rima")
    jihed_path = os.path.join(s.DATA_DIR, "jumla", "jihed")

    dhia_codes = os.listdir(dhia_path)
    rima_codes = os.listdir(rima_path)
    jihed_codes = os.listdir(jihed_path)
    combined_codes = os.listdir(combined_path)


    add_to_combined(combined_codes,dhia_codes,"dhia")
    add_to_combined(combined_codes,rima_codes,"rima")
    add_to_combined(combined_codes,jihed_codes,"jihed")



def convert_svo_mp4():
    combined_path = os.path.join(s.DATA_DIR, "jumla","combined")
    signs = os.listdir(combined_path)
    
    for sign in signs:
        sign_path = os.path.join(combined_path,sign)
        videos = os.listdir(sign_path)
        for video in videos:
            video_path = os.path.join(sign_path,video)
            dst_path = os.path.join(sign_path,f'{video.replace(".svo","")}.mp4')
            #print(video_path,"\n",dst_path)
            convert(video_path,dst_path)
            #os.system(command)
            exit()

    




def parse_args():
    parser = argparse.ArgumentParser(
        description='Download Jumla Dataset')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--map', action='store_true')
    parser.add_argument('--move-duplicates', action='store_true')
    parser.add_argument('--remove-duplicates', action='store_true')
    parser.add_argument('--create-combined', action='store_true')
    parser.add_argument('--combine-dataset', action='store_true')
    parser.add_argument('--convert-svo', action='store_true')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    global_args = parse_args()
    args.download = global_args.download
    args.map = global_args.map
    args.move_duplicates = global_args.move_duplicates
    args.remove_duplicates = global_args.remove_duplicates
    args.create_combined = global_args.create_combined
    args.combine_dataset = global_args.combine_dataset
    args.convert_svo = global_args.convert_svo

    if args.map == True:
        map_code_sign()
    elif args.download == True:
        download_vids()
    elif args.move_duplicates == True:
        move_duplicates()
    elif args.remove_duplicates == True:
        remove_duplicates()
    elif args.create_combined == True:
        create_combined_folder()
    elif args.combine_dataset == True:
        combine_dataset()
    elif args.convert_svo == True:
        convert_svo_mp4()
