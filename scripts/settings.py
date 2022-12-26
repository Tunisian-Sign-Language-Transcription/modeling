
import numpy as np
import os


FPS = 30

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR,'data')
JOINTS_DATA_DIR = os.path.join(DATA_DIR,'joints') 
MODELS_DIR = os.path.join(ROOT_DIR,'models')


SEQUENCE_COLLECTION_WAIT = 2000

ACTIONS = np.array(['sourd','rdv'])
NO_SEQUENCES = 10
SEQUENCE_LENGTH = 30
START_FOLDER = 1