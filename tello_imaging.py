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
#           tello_imaging.py
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
#    1.0     01/09/2023  Initial Release
#
#  File Description
#  ----------------
#  This allows for the tello to take multiple photos of a chessboard
#  and converts the results to a matrix
#  The photos are saved to a file with the drone's wifi name
#  *Classes/Functions organized by order of appearance
#
#  OUTSIDE FILES REQUIRED
#  ----------------------
#   wifi_testing.py
#   tello_remove_bad.py
#   tello_calibration.py
#
#  CLASSES
#  -------
#   None
#
#  FUNCTIONS
#  ---------
#   main
#
'''
#################################################################################################
#Import Statements
#################################################################################################

from djitellopy import tello
from datetime import datetime
import os
import argparse
import cv2
import time
import numpy as np  # alias
from wifi_testing import get_wifi_info
from tello_remove_bad import remove_bad_images
from tello_calibration import get_matrix
#################################################################################################
#Functions
#################################################################################################


def main(chessboard_size, frame_size, chessboard_square_size):
    """function that returns list of apriltag center coordinates
    Parameters
    ----------
    chessboard_size: tuple
        the number of interior corners of black squares on the chessboard
        width height
    frame_size
    chessboard_square_size

    a_tags: int
        a list of apriltags

    Returns
    -------
    a_tag_centers : list
        a list of centers of detected apriltags
    """

    #added tello_name 
    tello_name = get_wifi_info()
    telloimages_dir = f"telloImages_{tello_name}"
    if not os.path.exists(telloimages_dir):
        os.makedirs(telloimages_dir)
    tello_drone = tello.Tello()
    tello_drone.connect()
    battery = tello_drone.get_battery()
    print(f"Drone Battery: {battery}")
    tello_drone.streamon()  # camera on
    counter = 0

    #hopefully this doesn't break
    
    #hopefully this doesn't break(if does move to line 38)

    #break this loop after so many images
    #only take every 5 frames
    while True:
        framerad = tello_drone.get_frame_read()
        img = framerad.frame
        counter += 1
        if counter % 5 == 0:
            imageFileName = os.path.join(telloimages_dir,f"{tello_name}{datetime.now()}.png")
            cv2.imwrite(imageFileName,img)
            cv2.imshow("Image", img)
        keycode = cv2.waitKey(5)
        if (keycode & 0xFF) == ord('q'):
            break
        elif counter == 500:
            break
    tello_drone.streamoff()
    cv2.destroyAllWindows()
    remove_bad_images(tello_name, chessboard_size, frame_size)
    get_matrix(tello_name, chessboard_size, chessboard_square_size, frame_size)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chessboard_width", default=6, type=int)
    parser.add_argument("--chessboard_height", default=6, type=int)
    parser.add_argument("--chessboard_square_size", default=18, type=int)
    parser.add_argument("--width", default=960, type=int)
    parser.add_argument("--height", default=720, type=int)
    args = parser.parse_args()
    chessboard_size = (args.chessboard_width, args.chessboard_height)
    frame_size = (args.width, args.height)
    main(chessboard_size, frame_size, args.chessboard_square_size)
