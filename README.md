# Modeling
## Installation
### Virtual environement
```
conda create --name tsl-classification-envir python=3.8
conda activate tsl-classification-envir 
cd scripts
```
### Dependencies
```
pip install tensorflow==2.4.1 tensorflow-gpu==2.4.1 opencv-python mediapipe sklearn matplotlib
```


The scripts directory contains all needed scripts to prepare dataset, run pose detection on the cam and detect actions and to run the model

## Preparing the data
First, start by adding the words you want to classify to ACTIONS in scripts/settings.py like the example below

```python
ACTIONS = np.array(['word_1', 'word_2', 'word_3'])
```
You can set the number of sequences for each action and the length of each sequence (frames)

```python
NO_SEQUENCES = 10
SEQUENCE_LENGTH = 30
```

run the following script to generate the dataset directories in data/joints (always run the scripts from withtin the scripts directory
```
python data_preparation.py --init
```

if you want to clear actions in a folder use
```
python data_preparation.py --clear-actions
```

if you want to clear data 
```
python data_preparation.py --clear-data
```

## Collecting Data
Now that you have your directory ready, you can start collecting your datset using your cam by running the following script (the instructions will be inclded in the cam feed)
```
python cam.py --collect-data
```

you can also play a recorded sequence of a specific action by running the following command
```
python cam.py --play {ACTION} {SEQUENCE_NUMBER}
```


## Running the model
you can run the model on the collected dataset by executing this script (the model will be stored in the models directory)
```
python model.py --train <model_architecture> <model_name>
```
to Monitor the training performance of your model run this command within the scripts/Logs/train directory and then grab the generated url and put it in a browser
```
tensorboard --logdir=.
```

### Real Time testing
You can test the model once trained on real time feed of your webcam by running this command (make sure the model exists in models/ directory)

```
python cam.py --test <model_architecture> <model_name>
```
