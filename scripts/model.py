from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard
from scipy import stats
import argparse
import abc
import settings as s
import numpy as np
import os
#import tensorflowjs as tfjs
from transformer import *
from lstm import *

#from data_preparation import load_data

args = abc.abstractproperty()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Modeling')
    parser.add_argument('--train', action='store', nargs=2, type=str)
    parser.add_argument('--test', action='store', nargs=2, type=str)
    parser.add_argument('--dataset', action='store', nargs=1, type=str)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    global_args = parse_args()
    model = global_args.train[0]
    model_name = global_args.train[1]
    dataset = global_args.dataset[0]


    if dataset not in ['jumla', 'cam', 'saved']:
        print(f'Dataset doesn"t exist')
        exit()

    if model == 'transformer':
        train_transformer_model(model_name, dataset)
    elif model == 'lstm':
        train_lstm_pose_model(model_name, dataset)
    else:
        print("Not a valid model architecture.")
