

from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard
import numpy as np
import tensorflowjs as tfjs
import os 
from data_preparation import load_data
import settings as s


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


def train_lstm_pose_model(model_name):
    sequences, labels = load_data()
    X = np.array(sequences)
    y = to_categorical(labels).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=s.TRAIN_TEST_SPLIT)

    log_dir = os.path.join('Logs')
    tb_callback = TensorBoard(log_dir=log_dir)

    model = build_lstm_pose_model()
    model.compile(optimizer='Adam', loss='categorical_crossentropy',
                  metrics=['categorical_accuracy'])

    model.fit(X_train, y_train, epochs=s.LSTM_EPOCHS, callbacks=[tb_callback])
    model.save(os.path.join(s.MODELS_DIR, f'{model_name}.h5'))
    tfjs.converters.save_keras_model(model, s.MODELS_DIR)


def test():
    model = build_lstm_pose_model()
    model.load_weights('action.h5')