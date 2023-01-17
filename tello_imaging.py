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
#
#
#  CLASSES
#  -------
#   None
#
#  FUNCTIONS
#  ---------
#   get_matrix
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
import json
import numpy as np  # alias
from wifi_testing import get_wifi_info


#################################################################################################
#Functions
#################################################################################################


def get_matrix(tello_name, chessboard_size, frame_size, chessboard_square_size_mm):
    """function that creates the camera calibration  matrix

        Parameters
        ----------
        tello_name: string
             wifi name of the  tello drone in use
        chessboard_size: tuple
            As you move along a column or row,
            count the number of corners individual square colors excluding the perimeter  squares
        frame_size: tuple
            width and the height of the camera window in pixels
        chessboard_square_size_mm: int
            measurement of each individual black square in mm

        Returns
        -------
        None
        """
    img_location = f"telloImages_{tello_name}"

    ################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################


    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboard_size[0],0:chessboard_size[1]].T.reshape(-1,2)

    objp = objp * chessboard_square_size_mm


    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    counter = 0

    print("Begin loading images")
    img_locationList = os.listdir(img_location)
    #if this breaks use glob
    for afile in img_locationList:
        if afile.endswith(".png"):

            print(f"image {counter} of {len(os.listdir(img_location))} was loaded\n")
            img = cv2.imread(os.path.join(img_location, afile))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)
                #corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners)
        counter +=1


    ############## CALIBRATION #######################################################
    print("Begin camera calibration")
    ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints,
        frame_size, None, None)
    print("end camera calibration")

    ############## UNDISTORTION #####################################################
    #get first image in image_directory for cropping
    counter = 0
    #gets first file(should be image) in the image location, and crops for newcameramatrix
    img = cv2.imread(os.path.join(img_location, img_locationList[0]))
    h,  w = img.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
    #print(newCameraMatrix)
    print("Begin writing matrix file")

    out_camera_matrix = {'fx': newCameraMatrix[0][0], 'cx': newCameraMatrix[0][2], 'fy': newCameraMatrix[1][1],
                            'cy': newCameraMatrix[1][2]}
    out_camera_matrix_json = json.dumps(out_camera_matrix, indent=4)

    with open(f'camera_matrix_{tello_name}.json', 'w') as f:
        f.write(out_camera_matrix_json)

    # Reprojection Error
    mean_error = 0

    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], newCameraMatrix, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error

    print( "total error: {}".format(mean_error/len(objpoints)) )

    cv2.destroyAllWindows()






def main(chessboard_size, frame_size, chessboard_square_size_mm):
    """function that returns list of apriltag center coordinates

    Parameters
    ----------
    chessboard_size: tuple
        As you move along a column or row,
        count the number of corners individual square colors excluding the perimeter  squares
    frame_size: tuple
        width and the height of the camera window in pixels
    chessboard_square_size_mm: int
        measurement of each individual black square in mm

    Returns
    -------
    None
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
    


    while True:
        framerad = tello_drone.get_frame_read()
        img = framerad.frame
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, _ = cv2.findChessboardCorners(gray, chessboard_size, None)
        if ret:
            imageFileName = os.path.join(telloimages_dir,f"{tello_name}{datetime.now()}.png")
            cv2.imwrite(imageFileName,img)
            cv2.imshow("Image", img)
            keycode = cv2.waitKey(5)
            if (keycode & 0xFF) == ord('q'):
                break
        time.sleep(5)
    tello_drone.streamoff()
    cv2.destroyAllWindows()
    get_matrix(tello_name, chessboard_size, frame_size, chessboard_square_size_mm)
    
    
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
