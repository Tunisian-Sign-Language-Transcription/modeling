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

import settings as s
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


def convert(input_path, output_path):
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

    nb_frames = zed.get_svo_number_of_frames()

    x = nb_frames // s.SEQUENCE_LENGTH

    counter = 1

    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while True:
            if zed.grab(rt_param) == sl.ERROR_CODE.SUCCESS:
                svo_position = zed.get_svo_position()
                
                # Retrieve SVO images
                zed.retrieve_image(left_image, sl.VIEW.LEFT)
                zed.retrieve_image(right_image, sl.VIEW.RIGHT)
                # Generate file names
                filename1 = os.path.join(
                    output_path, ("left%s" % str(svo_position).zfill(6)))
                # Save Left images

                if svo_position % x == 0:            
                    image, results = mediapipe_detection(
                        left_image.get_data(), holistic)
                    keypoints = extract_keypoints(results)
                    np.save(os.path.join(output_path, str(counter)), keypoints)
                    counter += 1

                progress_bar((svo_position + 1) / nb_frames * 100, 30)

                if svo_position >= (nb_frames - 1):  # End of SVO
                    break

    zed.close()
    return 0
