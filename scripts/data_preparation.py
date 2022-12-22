
import os
import settings as s
import argparse
import abc
import shutil
import glob
args = abc.abstractproperty()



def prepare_data_directories():
    for action in s.ACTIONS:
        path = os.path.join(s.JOINTS_DATA_DIR,action)
        for sequence in range(1,s.NO_SEQUENCES+1):
            try: 
                os.makedirs(os.path.join(path,str(sequence)))
            except:
                pass



def clear_actions():
    for action in s.ACTIONS:
        path = os.path.join(s.JOINTS_DATA_DIR,action)
        if os.path.exists(path):
            shutil.rmtree(path)

def clear_data():
    for action in s.ACTIONS:
        for sequence in range(1,s.NO_SEQUENCES+1):
            for frame in range(1,s.SEQUENCE_LENGTH+1):
                path = os.path.join(s.JOINTS_DATA_DIR,action,str(sequence),f'{frame}.npy')
                if os.path.exists(path):
                    os.remove(path)



def parse_args():
    parser = argparse.ArgumentParser(
        description='Data Preparation')
    parser.add_argument('--prepare-directories', action='store_true')
    parser.add_argument('--clear-data', action='store_true')
    parser.add_argument('--clear-actions', action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    global_args = parse_args()
    args.prepare_directories = global_args.prepare_directories
    args.clear_data = global_args.clear_data
    args.clear_actions = global_args.clear_actions

    if args.clear_actions == True:
        clear_actions()
    elif args.prepare_directories:
        prepare_data_directories()
    elif args.clear_data:
        clear_data()