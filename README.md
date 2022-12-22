# modeling
Start by setting up the environment

```
pip install tensorflow==2.4.1 tensorflow-gpu==2.4.1 opencv-python mediapipe sklearn matplotlib
```

The scripts directory contains all needed scripts to prepare dataset, run pose detection on the cam and detect actions and to run the model

## Preparing the data
First, start by adding the words you want to classify to ACTIONS in scripts/settings.py like the example above

```python
ACTIONS = np.array(['word_1', 'word_2', 'word_3'])
```

run the following script to generate the dataset directories in data/joints (always run the scripts from withtin the scripts directory
```
python data_preparation --prepare-directories
```

if you want to clear actions in a folder use
```
python data_preparation --clear-actions
```

if you want to clear data 
```
python data_preparation --prepare-data
```

## Collecting Data
Now that you have your directory ready, you can start collecting your datset using your cam by running the following script (the instructions will be inclded in the cam feed)
```
python cam.py --collect-data
```

## Running the model
you can run the model on the collected dataset by executing this script (the model will be stored in the models directory)
```
python model.py 
```
