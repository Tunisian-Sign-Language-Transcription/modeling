
import os
import settings as s
import argparse
import abc
import shutil
import glob
import numpy as np

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



def load_data(source="cam"):
    
    sequences, labels = [], []

    if (source == "saved"):
        actions = s.SAVED_ACTIONS
        joints_trg = s.SAVED_JOINTS_DATA_DIR
    elif (source == "cam"):
        actions = s.ACTIONS
        joints_trg = s.JOINTS_DATA_DIR
    else:
        print("Source not specified.")
        exit()

    label_map = {label: num for num, label in enumerate(actions)}
    for action in actions:
        for sequence in np.array(os.listdir(os.path.join(joints_trg,action))).astype(int):
            window = []
            for frame_num in range(1, s.SEQUENCE_LENGTH+1):
                res = np.load(os.path.join(joints_trg,action,str(sequence),f'{frame_num}.npy'))
                window.append(res)

            sequences.append(window)
            labels.append(label_map[action])


    return sequences, labels


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