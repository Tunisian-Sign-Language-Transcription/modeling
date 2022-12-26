
import os
import settings as s
import argparse
import abc
import shutil
import glob
args = abc.abstractproperty()



def prepare_data_directories():
    for dir in ["joints","saved"]:
        for action in s.ACTIONS:
            path = os.path.join(s.DATA_DIR,dir,action)
            for sequence in range(1,s.NO_SEQUENCES+1):
                try: 
                    os.makedirs(os.path.join(path,str(sequence)))
                except:
                    pass



def clear_actions():
    for dir in ["joints","saved"]:
        for action in os.listdir(os.path.join(s.DATA_DIR,dir)):
            path = os.path.join(s.DATA_DIR,dir,action)
            if os.path.exists(path) and os.path.isdir(path):
                shutil.rmtree(path)


def clear_data():
    for dir in ["joints","saved"]:
        for action in s.ACTIONS:
            for sequence in range(1,s.NO_SEQUENCES+1):
                for frame in range(1,s.SEQUENCE_LENGTH+1):
                    if dir == "joints":
                        path = os.path.join(s.DATA_DIR,dir,action,str(sequence),f'{frame}.npy')
                    else:
                        path = os.path.join(s.DATA_DIR,dir,action,str(sequence),f'{frame}.jpg')
                    if os.path.exists(path):
                        os.remove(path)



def parse_args():
    parser = argparse.ArgumentParser(
        description='Data Preparation')
    parser.add_argument('--init', action='store_true')
    parser.add_argument('--clear-data', action='store_true')
    parser.add_argument('--clear-actions', action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    global_args = parse_args()
    args.init = global_args.init
    args.clear_data = global_args.clear_data
    args.clear_actions = global_args.clear_actions

    if args.clear_actions == True:
        clear_actions()
    elif args.init:
        prepare_data_directories()
    elif args.clear_data:
        clear_data()