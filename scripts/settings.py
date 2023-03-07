
import numpy as np
import os



FPS = 30

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR,'data')
JOINTS_DATA_DIR = os.path.join(DATA_DIR,'joints') 
MODELS_DIR = os.path.join(ROOT_DIR,'models')

SAVED_JOINTS_DATA_DIR = os.path.join(DATA_DIR,'saved','joints')


SEQUENCE_COLLECTION_WAIT = 2000

ACTIONS = np.array([''])

SAVED_ACTIONS = np.array(['test'])

NO_SEQUENCES = 10
SEQUENCE_LENGTH = 30
START_FOLDER = 1


TRAIN_TEST_SPLIT = 0.05


## LSTM Hyperparameters

LSTM_EPOCHS = 30


## Transfomer Hyperparameters

MAXLEN = 30     # Only consider the first 30 frames of each sequence

EMBED_DIM = 258 # Embedding size of each token
NUM_HEADS = 2   # Number of attention heads 
FF_DIM = 32     # Hidden layer size in feed forward network
TRANSFORMER_EPOCHS = 30

