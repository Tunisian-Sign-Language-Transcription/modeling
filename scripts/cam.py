import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
import argparse
import abc

from extract_joints import mediapipe_detection, extract_keypoints, save_keypoints
import settings as s

args = abc.abstractproperty()
mp_holistic = mp.solutions.holistic 
mp_drawing = mp.solutions.drawing_utils 



def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION) 
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS) 
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS) 
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS) 


def draw_styled_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION, 
                             mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1), 
                             mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                             ) 
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                             mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                             ) 
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                             ) 
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                             mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), 
                             mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                             ) 



def display(draw_joints=False,draw_styled_joints=False):
    
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if draw_joints == True or draw_styled_joints==True:
                image, results = mediapipe_detection(frame, holistic)
                if draw_styled_joints:
                    draw_styled_landmarks(image, results)
                else:
                    draw_landmarks(image,results)
            else:
                image = frame

            cv2.imshow('OpenCV Feed', image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break


        cap.release()
        cv2.destroyAllWindows()





def parse_args():
    parser = argparse.ArgumentParser(
        description='Display Real Time Joints')
    parser.add_argument('--draw-joints', action='store_true')
    parser.add_argument('--draw-styled-joints', action='store_true')
    parser.add_argument('--collect-data', action='store_true')
    args = parser.parse_args()
    return args

def collect_data():
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        for action in s.ACTIONS:
            for sequence in range(s.START_FOLDER,s.START_FOLDER+s.NO_SEQUENCES):
                for frame_num in range(1,s.SEQUENCE_LENGTH+1):
                    ret, frame = cap.read()
                    image, results = mediapipe_detection(frame,holistic)
                    draw_styled_landmarks(image,results)

                    if frame_num ==0:
                        cv2.putText(image, 'STARTING COLLECTION', (120,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
                        cv2.putText(image,f'Collecting frames for {action} video Number {sequence}',(15,12),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.imshow('OpenCV Feed', image)
                        cv2.waitKey(500)
                    else:
                        cv2.putText(image,f'Collecting frames for {action} video Number {sequence}',(15,12),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                        cv2.imshow('OpenCV Feed', image)
                    keypoints = extract_keypoints(results)
                    save_keypoints(action,sequence,frame_num,keypoints)
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break
                    

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    global_args = parse_args()
    args.draw_joints = global_args.draw_joints
    args.draw_styled_joints = global_args.draw_styled_joints
    args.collect_data = global_args.collect_data
    if args.collect_data==True:
        collect_data()
    else:
        display(args.draw_joints,args.draw_styled_joints)
