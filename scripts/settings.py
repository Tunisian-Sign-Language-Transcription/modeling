
import numpy as np
import os


FPS = 30

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR,'data')
JOINTS_DATA_DIR = os.path.join(DATA_DIR,'joints') 
MODELS_DIR = os.path.join(ROOT_DIR,'models')

SAVED_JOINTS_DATA_DIR = os.path.join(DATA_DIR,'saved','joints')


SEQUENCE_COLLECTION_WAIT = 2000

ACTIONS = np.array(['sourd' ,'rdv'])

SAVED_ACTIONS = np.array(['test'])

NO_SEQUENCES = 2
SEQUENCE_LENGTH = 30
START_FOLDER = 1