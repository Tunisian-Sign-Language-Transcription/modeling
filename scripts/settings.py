
import numpy as np
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR,'data')
JOINTS_DATA_DIR = os.path.join(DATA_DIR,'joints') 
MODELS_DIR = os.path.join(ROOT_DIR,'models')



ACTIONS = np.array(['hello', 'thanks', 'iloveyou'])
NO_SEQUENCES = 3
SEQUENCE_LENGTH = 30
START_FOLDER = 1