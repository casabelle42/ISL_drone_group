'''
#################################################################################################
#
#
#   Fayetteville State University Intelligence Systems Laboratory (FSU-ISL)
#
#   Mentors:
#           Dr. Sambit Bhattacharya
#           Catherine Spooner
#
#   File Name:
#           drone_flight.py
#
#   Programmers:
#           Antonio Ball
#           Ryan De Jesus
#           Garrett Davis
#           Kalsoom Bibi
#           Santino Sini
#           Daniel Bigler
#           Taryn Rozier
#           Ashley Sutherland
#           Tyuss Handley
#           Adriel Alvarez
#           Malik Brock
#           Raymond Poythress
#
#  Revision     Date                        Release Comment
#  --------  ----------  ------------------------------------------------------
#    1.0     01/12/2023  Initial Release
#
#  File Description
#  ----------------
#  This program navigates drone towards april tags
#  
#   
#  
#  
#  
#  *Classes/Functions organized by order of appearance
#
#  OUTSIDE FILES REQUIRED
#  ----------------------
#   wifi_testing.py
#   
#
#  CLASSES
#  -------
#   None
#
#  FUNCTIONS
#  ---------
#   get_wifi_info
#   main
#
'''
#################################################################################################
#Import Statements
#################################################################################################
import os.path
from djitellopy import tello
from datetime import datetime
import argparse
import pupil_apriltags as apriltags  # alias for apriltags
import cv2
import numpy as np  # alias
import time
import json
from math import sqrt

from wifi_testing import get_wifi_info

#################################################################################################
#Functions
#################################################################################################

def get_distance_to_camera(irl_width, focal_length, pixel_width):
    """function that returns the distance from a measured to camera
    Parameters
    ----------
    irl_width: float
        real life width of the marker
    focal_length: float
        focal length of camera
    pixel_width: int
        perceived width of marker in pixels

    Returns
    -------
    distance: float
        distance from marker to camera
    """
    #Returns in meters
    distance_meters = (irl_width * focal_length) / pixel_width
    distance = distance_meters * 100
    return distance

def show_distance(img, distance):
    distance_in_video = cv2.putText(img, str(distance), (20, 80), cv2.FONT_HERSHEY_COMPLEX, 1, (40, 0, 255), 2)
    return distance_in_video

def get_apriltag_coords(a_tags):

    """function that returns list of apriltag center coordinates
    Parameters
    ----------
    a_tags: list
        a list of apriltags

    Returns
    -------
    a_tag_centers : list
        a list of centers of detected apriltags
    """

    a_tag_centers = []
    for tag in a_tags:
        cX, cY = (int(tag.center[0]), int(tag.center[1]))
        # list with centers of apriltags
        a_tag_centers.append([cX, cY])
    return a_tag_centers


def find_box(a_tag):
    """function that will find the corners of the april tag
    Parameters
    ----------
    a_tag: object
        a simple april tag

    Returns
    -------
    four_corners : tuple
        four corners of the april tag
    """

    ptA, ptB, ptC, ptD = a_tag.corners
    ptA = (int(ptA[0]), int(ptA[1]))
    ptB = (int(ptB[0]), int(ptB[1]))
    ptC = (int(ptC[0]), int(ptC[1]))
    ptD = (int(ptD[0]), int(ptD[1]))
    four_corners = (ptA, ptB, ptC, ptD)
    return four_corners


def read_apriltags(frame, camera_matrix, marker_width):
    """function that will provide apriltag detector results
    Parameters
    ----------

    frame: image
        image to detect apriltags in

    estimage_tag : boolean
        flag to estimate tag pos

    camera_pars : list
        list of camera parameters to estimate the tag pos
    Returns
    -------
    results : object
        apriltag detection results
    """
    if len(camera_matrix) == 0:
        estimate_tag = False
        camera_pars = None
    else:
        estimate_tag = True
        camera_pars = [camera_matrix['fx'], camera_matrix['fy'], camera_matrix['cx'], camera_matrix['cy']]
        detector = apriltags.Detector(families='tag36h11')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = detector.detect(gray, estimate_tag_pose=estimate_tag, camera_params=camera_pars, tag_size=marker_width)
    return results


def get_direction(centerX, centerY, img, frameWidth, frameHeight, deadZone):
    """function that returns the direction the drone should move in
    ----------

    centerX : int
        the center of the image on the x-axis

    centerY : int
        the center of the image on the y-axis

    img : array
        a camera image

    frameWidth : int
        width of camera image

    frameHeight: int
        height of camera image

    deadZone: int
        a margin of error for the center calculation

    Returns
    -------
    dir: int
        a numeric value that indicates which direction the drone should move
    """
    dir = 0
    if (centerX < int(frameWidth / 2) - deadZone):
        cv2.putText(img, " GO LEFT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        dir = 1
    elif (centerX > int(frameWidth / 2) + deadZone):
        cv2.putText(img, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        dir = 2
    elif (centerY < int(frameHeight / 2) - deadZone):
        cv2.putText(img, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        dir = 3
    elif (centerY > int(frameHeight / 2) + deadZone):
        cv2.putText(img, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        dir = 4
    return dir


def main(file_path, fps, width, height, marker_width, tello_name, camera_matrix):
    """function that will provide apriltag detector results
    Parameters
    ----------

    file_path : string
        full directory path to where the video file will be created.
        Default is None, so will create a datetime timestamp and create
        the file in current directory

    fps : int
        the number of frames per second for video capture and writing

    width : int
        width of camera image

    height : int
        height of camera image

    marker_width: float 
        the distance between point A and point B on an Apriltag

    NEED TO FINISH MODIFYING.
    tello_name: string
        the wifi name of the Tello

    camera_matrix: dictionary
        calibration matrix 
    

    Returns
    -------
    None
    """
    # CONSTANTS
    DEADZONE = 100
    # Variables
    

    focal_length = sqrt(camera_matrix["fx"] ** 2 + camera_matrix["fy"] ** 2)

    # create the video writer
    FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, FOURCC, fps, (width, height), True)

    # Counter
    testDrone = True  # False for flight, True for testing (flight disabled)

    # connect to the tello
    drone = tello.Tello()
    drone.connect()
    battery = drone.get_battery()

    print(f"Drone Battery: {battery}")

    drone.streamon()  # camera on
    time.sleep(2)
    if not testDrone:
        drone.takeoff()

    frame_counter = 0
    while True:

        framerad = drone.get_frame_read()
        img = framerad.frame
        results = read_apriltags(img, camera_matrix, marker_width)
        centerCAM = (int(width / 2), int(height / 2))
        direction = 0

        # SEND VELOCITY VALUES TO TELLO
        if results:
            print(f"frame {frame_counter}")
            if len(results) == 1:
                pA, pB, pC, pD = find_box(results[0])
                # get width of box corners (pA, pB)
                corner_width = abs(np.subtract(pB, pA))
                corner_width = sqrt(corner_width[0]**2 + corner_width[1]**2)
                marker_distance = get_distance_to_camera(marker_width, focal_length, corner_width)
                show_distance(img, marker_distance)
                print("marker distance", marker_distance)
                
                centerX = int(results[0].center[0])
                centerY = int(results[0].center[1])
                cv2.line(img, (centerX, centerY), centerCAM, (123, 255, 123), 2)
                cv2.circle(img, (centerX, centerY), 5, (255, 30, 12), -1)
                direction = get_direction(centerX, centerY, img, width, height, DEADZONE)
                print(f"rotational matrix \n {results[0].pose_R}")
                print(f"translational matrix \n {results[0].pose_t}")

        frame_counter += 1

        if direction == 1:
            drone.left_right_velocity = -20

        elif direction == 2:
            drone.left_right_velocity = 20

        elif direction == 3:
            drone.up_down_velocity = 20

        elif direction == 4:
            drone.up_down_velocity = -20

        else:
            drone.left_right_velocity = 0
            drone.for_back_velocity = 0
            drone.up_down_velocity = 0
            drone.yaw_velocity = 0

        # SEND VELOCITY VALUES TO TELLO
        if drone.send_rc_control:
            drone.send_rc_control(drone.left_right_velocity, drone.for_back_velocity, drone.up_down_velocity,
                                  drone.yaw_velocity)
        print(dir)

        cv2.circle(img, centerCAM, 5, (20, 30, 12), -1)
        # if drone is centered change gate square from blue to green

        out.write(img)
        cv2.imshow("Image", img)
        keycode = cv2.waitKey(5)
        if (keycode & 0xFF) == ord('q'):
            # tello.land()
            break

    out.release()
    drone.streamoff()

    drone.land()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    tello_name = get_wifi_info()
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default=None, help='path to filename for video')
    parser.add_argument("--fps", type=int, default=30, help="frames per second for video")
    parser.add_argument("--width", type=int, default=960, help="width of camera image")
    parser.add_argument("--height", type=int, default=720, help="height of camera image")
    parser.add_argument("--marker_width", type=float, default=0.038, help="physical size of the marker in meters")
    parser.add_argument("--matrix_file", type=str, default=None, help ="file name of the camera matrix")
    args = parser.parse_args()

    if args.filename is None:
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M")  # Format DateTime
        file_path = f"{tello_name}_apriltag_detections_{dt_string}.mp4"  # added DateTime for TimeStamp
    else:
        file_path = args.filename

    if args.matrix_file is None:
        json_path = f"camera_matrix_{tello_name}.json"
        if os.path.exists(json_path):
            with open(json_path) as f:
                camera_matrix = json.load(f)
        else:
            camera_matrix = {}
    else:
        if os.path.exists(args.matrix_file):
            with open(args.matrix_file) as f:
                camera_matrix = json.load(f)
        else:
            print("Could not locate specified file, sending empty matrix")
            camera_matrix = {}

    

    main(file_path, args.fps, args.width, args.height, args.marker_width, tello_name, camera_matrix)


