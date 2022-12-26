import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
import argparse
import abc
from model import *


from extract_joints import mediapipe_detection, extract_keypoints, save_keypoints
from model import load_data
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




def play_sequence(action,sequence_num):
    frames = []
    sequence_path = os.path.join(s.DATA_DIR,"saved",action,str(sequence_num))
    for frame in os.listdir(sequence_path):
        frame_path = os.path.join(sequence_path,frame)
        frames.append(cv2.imread(frame_path))
        frames.append(cv2.imread(frame_path))
        frames.append(cv2.imread(frame_path))
        frames.append(cv2.imread(frame_path))
        frames.append(cv2.imread(frame_path))

    for frame in frames:
        cv2.imshow(f'Playing {action} - {sequence_num}', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    

def collect_data():
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        for action in s.ACTIONS:
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            ret, frame = cap.read()


            cv2.putText(frame, f'STARTING COLLECTION for {action}', (120,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
            cv2.imshow('OpenCV Feed', frame)
            cv2.waitKey(s.SEQUENCE_COLLECTION_WAIT)


            for sequence in range(s.START_FOLDER,s.START_FOLDER+s.NO_SEQUENCES):
                ret, frame = cap.read()


                cv2.putText(frame, f'SEQUENCE  {sequence}', (120,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
                cv2.imshow('OpenCV Feed', frame)
                cv2.waitKey(s.SEQUENCE_COLLECTION_WAIT)


                for frame_num in range(1,s.SEQUENCE_LENGTH+1):
                    ret, frame = cap.read()
                    image, results = mediapipe_detection(frame,holistic)
                    draw_styled_landmarks(image,results)
                    
                    cv2.putText(image,f'Collecting frames for {action} video Number {sequence} frame {frame_num}',(15,12),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.imshow('OpenCV Feed', image)
                    keypoints = extract_keypoints(results)
                    save_keypoints(action,sequence,frame_num,keypoints)

                    saved_path = os.path.join(s.DATA_DIR,"saved",action,str(sequence),f'{frame_num}.jpg')
                    #print(path)
                    cv2.imwrite(saved_path, image) 


                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break
                    

        cap.release()
        cv2.destroyAllWindows()



colors = [(245,117,16), (117,245,16), (16,117,245)]
def prob_viz(res, actions, input_frame, colors):
    output_frame = input_frame.copy()
    for num, prob in enumerate(res):
        cv2.rectangle(output_frame, (0,60+num*40), (int(prob*100), 90+num*40), colors[num], -1)
        cv2.putText(output_frame, actions[num], (0, 85+num*40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        
    return output_frame

def test():
    sequence = []
    sentence = []
    predictions = []
    threshold = 0.5

    model = model_structure()
    model.load_weights(os.path.join(s.MODELS_DIR,'test.h5'))

    cap = cv2.VideoCapture(0)
    # Set mediapipe model 
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():

            # Read feed
            ret, frame = cap.read()

            # Make detections
            image, results = mediapipe_detection(frame, holistic)
            print(results)
            
            # Draw landmarks
            draw_styled_landmarks(image, results)
            
            # 2. Prediction logic
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            sequence = sequence[-30:]
            
            if len(sequence) == 30:
                res = model.predict(np.expand_dims(sequence, axis=0))[0]
                print(s.ACTIONS[np.argmax(res)])
                predictions.append(np.argmax(res))
                
                
            #3. Viz logic
                if np.unique(predictions[-10:])[0]==np.argmax(res): 
                    if res[np.argmax(res)] > threshold: 
                        
                        if len(sentence) > 0: 
                            if s.ACTIONS[np.argmax(res)] != sentence[-1]:
                                sentence.append(s.ACTIONS[np.argmax(res)])
                        else:
                            sentence.append(s.ACTIONS[np.argmax(res)])

                if len(sentence) > 5: 
                    sentence = sentence[-5:]

                # Viz probabilities
                image = prob_viz(res, s.ACTIONS, image, colors)
                
            cv2.rectangle(image, (0,0), (640, 40), (245, 117, 16), -1)
            cv2.putText(image, ' '.join(sentence), (3,30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Show to screen
            cv2.imshow('OpenCV Feed', image)

            # Break gracefully
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
    parser.add_argument('--play',action = "store",nargs=2, type=str)
    parser.add_argument('--test',action = "store_true")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    global_args = parse_args()
    args.draw_joints = global_args.draw_joints
    args.draw_styled_joints = global_args.draw_styled_joints
    args.collect_data = global_args.collect_data
    args.play = global_args.play
    args.test = global_args.test
    if args.play is not None:
        play_sequence(args.play[0],int(args.play[1]))
    elif  args.collect_data==True:
        collect_data()
    elif args.test == True:
        test()
    else:
        display(args.draw_joints,args.draw_styled_joints)
