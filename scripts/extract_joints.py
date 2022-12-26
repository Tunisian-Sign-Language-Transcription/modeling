import mediapipe as mp
import cv2
from matplotlib import pyplot as plt
import numpy as np
import settings as s
import os

mp_holistic = mp.solutions.holistic 

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
    image.flags.writeable = False                  
    results = model.process(image)                 
    image.flags.writeable = True                   
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) 
    return image, results



def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    #face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])


def save_keypoints(action,sequence,frame,keypoints):
    filename = os.path.join(action,str(sequence),str(frame))
    full_file_path = os.path.join(s.JOINTS_DATA_DIR,filename)
    np.save(full_file_path, keypoints)



if __name__ == '__main__':
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imshow('Test', frame)

        image, results = mediapipe_detection(frame, holistic)
        
        save_keypoints("test",results)

        if cv2.waitKey(0) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()