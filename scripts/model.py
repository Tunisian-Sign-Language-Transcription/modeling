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
import tensorflowjs as tfjs
from transformer import *
from lstm import *

#from data_preparation import load_data

args = abc.abstractproperty()



def parse_args():
    parser = argparse.ArgumentParser(
        description='Modeling')
    parser.add_argument('--train', action='store', nargs=2, type=str)
    parser.add_argument('--test', action='store', nargs=2, type=str)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    global_args = parse_args()
    args.train = global_args.train
    args.test = global_args.test

    if args.train is not None:
        if args.train[0] == 'transformer':
            train_transformer_model(args.train[1])
        elif args.train[0] == 'lstm':
            train_lstm_pose_model(args.train[1])
        else:
            print("Not a valid model architecture.")

