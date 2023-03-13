########################################################################
#
# Copyright (c) 2022, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

import sys
import pyzed.sl as sl
import numpy as np
import cv2
from pathlib import Path
import enum
import os
from extract_joints import mediapipe_detection, extract_keypoints, save_keypoints
import mediapipe as mp
mp_holistic = mp.solutions.holistic 


class AppType(enum.Enum):
    LEFT_AND_RIGHT = 1
    LEFT_AND_DEPTH = 2
    LEFT_AND_DEPTH_16 = 3


def progress_bar(percent_done, bar_length=50):
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %f%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()



def convert(input_path,output_path):
    svo_input_path = input_path
    output_path = output_path

    init_params = sl.InitParameters()
    init_params.set_from_svo_file(str(svo_input_path))

    zed = sl.Camera()

    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        sys.stdout.write(repr(err))
        zed.close()
        exit()

    image_size = zed.get_camera_information().camera_resolution
    width = image_size.width

    left_image = sl.Mat()
    right_image = sl.Mat()



    rt_param = sl.RuntimeParameters()
    rt_param.sensing_mode = sl.SENSING_MODE.FILL

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")

    nb_frames = zed.get_svo_number_of_frames()

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while True:
            if zed.grab(rt_param) == sl.ERROR_CODE.SUCCESS:
                svo_position = zed.get_svo_position()
                # Retrieve SVO images
                zed.retrieve_image(left_image, sl.VIEW.LEFT)
                zed.retrieve_image(right_image, sl.VIEW.RIGHT)
                # Generate file names
                filename1 = os.path.join(output_path,("left%s" % str(svo_position).zfill(6)))
                # Save Left images

                if svo_position % 10 == 0:
                    image, results = mediapipe_detection(left_image.get_data(),holistic)
                    keypoints = extract_keypoints(results)
                    np.save(filename1,keypoints)
                    #cv2.imwrite(str(filename1), left_image.get_data())
                # Display progress
                progress_bar((svo_position + 1) / nb_frames * 100, 30)

                # Check if we have reached the end of the video
                if svo_position >= (nb_frames - 1):  # End of SVO
                    sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
                    break


    zed.close()
    return 0


def convert_(input_path, output_path):
    
    # Get input parameters
    svo_input_path = input_path
    output_path = output_path
    output_as_video = False    
    app_type = AppType.LEFT_AND_RIGHT
    
    
        
    
    

    # Specify SVO path parameter
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(str(svo_input_path))
    init_params.svo_real_time_mode = False  # Don't convert in realtime
    init_params.coordinate_units = sl.UNIT.MILLIMETER  # Use milliliter units (for depth measurements)

    # Create ZED objects
    zed = sl.Camera()

    # Open the SVO file specified as a parameter
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        sys.stdout.write(repr(err))
        zed.close()
        exit()
    
    # Get image size
    image_size = zed.get_camera_information().camera_resolution
    width = image_size.width
    height = image_size.height
    width_sbs = width * 2
    
    # Prepare side by side image container equivalent to CV_8UC4
    svo_image_sbs_rgba = np.zeros((height, width_sbs, 4), dtype=np.uint8)

    # Prepare single image containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_image = sl.Mat()

    video_writer = None
    if output_as_video:
        # Create video writer with MPEG-4 part 2 codec
        video_writer = cv2.VideoWriter(str(output_path),
                                       cv2.VideoWriter_fourcc('M', '4', 'S', '2'),
                                       max(zed.get_camera_information().camera_fps, 25),
                                       (width_sbs, height))

        if not video_writer.isOpened():
            sys.stdout.write("OpenCV video writer cannot be opened. Please check the .avi file path and write "
                             "permissions.\n")
            zed.close()
            exit()
    
    rt_param = sl.RuntimeParameters()
    rt_param.sensing_mode = sl.SENSING_MODE.FILL

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")

    nb_frames = zed.get_svo_number_of_frames()

    while True:
        if zed.grab(rt_param) == sl.ERROR_CODE.SUCCESS:
            svo_position = zed.get_svo_position()

            # Retrieve SVO images
            zed.retrieve_image(left_image, sl.VIEW.LEFT)

            if app_type == AppType.LEFT_AND_RIGHT:
                zed.retrieve_image(right_image, sl.VIEW.RIGHT)
            elif app_type == AppType.LEFT_AND_DEPTH:
                zed.retrieve_image(right_image, sl.VIEW.DEPTH)
            elif app_type == AppType.LEFT_AND_DEPTH_16:
                zed.retrieve_measure(depth_image, sl.MEASURE.DEPTH)

            if output_as_video:
                # Copy the left image to the left side of SBS image
                svo_image_sbs_rgba[0:height, 0:width, :] = left_image.get_data()

                # Copy the right image to the right side of SBS image
                svo_image_sbs_rgba[0:, width:, :] = right_image.get_data()

                # Convert SVO image from RGBA to RGB
                ocv_image_sbs_rgb = cv2.cvtColor(svo_image_sbs_rgba, cv2.COLOR_RGBA2RGB)

                # Write the RGB image in the video
                video_writer.write(ocv_image_sbs_rgb)
            else:
                # Generate file names
                filename1 = os.path.join(output_path,("left%s.png" % str(svo_position).zfill(6)))
                filename2 = os.path.join(output_path, (("right%s.png" if app_type == AppType.LEFT_AND_RIGHT
                                           else "depth%s.png") % str(svo_position).zfill(6)))
                
                # Save Left images
                cv2.imwrite(str(filename1), left_image.get_data())

                """if app_type != AppType.LEFT_AND_DEPTH_16:
                    # Save right images
                    cv2.imwrite(str(filename2), right_image.get_data())
                else:
                    # Save depth images (convert to uint16)
                    cv2.imwrite(str(filename2), depth_image.get_data().astype(np.uint16))"""

            # Display progress
            progress_bar((svo_position + 1) / nb_frames * 100, 30)

            # Check if we have reached the end of the video
            if svo_position >= (nb_frames - 1):  # End of SVO
                sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
                break

    if output_as_video:
        # Close the video writer
        video_writer.release()

    zed.close()
    return 0

