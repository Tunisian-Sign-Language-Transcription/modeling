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

args = abc.abstractproperty()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Modeling')
    parser.add_argument('--prepare-directories', action='store_true')
    parser.add_argument('--clear-data', action='store_true')
    parser.add_argument('--clear-actions', action='store_true')
    args = parser.parse_args()
    return args


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



def build_lstm_pose_model():
    model = Sequential()
    model.add(LSTM(64, return_sequences=True,
              activation='relu', input_shape=(30, 258)))
    model.add(LSTM(128, return_sequences=True, activation='relu'))
    model.add(LSTM(64, return_sequences=False, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(s.ACTIONS.shape[0], activation='softmax'))
    return model


def train(model_name):
    sequences, labels = load_data()
    X = np.array(sequences)
    y = to_categorical(labels).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05)

    log_dir = os.path.join('Logs')
    tb_callback = TensorBoard(log_dir=log_dir)

    model = build_lstm_pose_model()
    model.compile(optimizer='Adam', loss='categorical_crossentropy',
                  metrics=['categorical_accuracy'])

    model.fit(X_train, y_train, epochs=2000, callbacks=[tb_callback])
    model.save(os.path.join(s.MODELS_DIR, f'{model_name}.h5'))
    tfjs.converters.save_keras_model(model, s.MODELS_DIR)


def test():
    model = build_lstm_pose_model()
    model.load_weights('action.h5')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Modeling')
    parser.add_argument('--train', action='store', nargs=1, type=str)
    parser.add_argument('--test', action='store', nargs=2, type=str)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    global_args = parse_args()
    args.train = global_args.train
    args.test = global_args.test

    if args.train is not None:
        train(args.train)
    elif args.test is not None:
        test()
