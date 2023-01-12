import numpy as np
import cv2
import os
from wifi_testing import get_wifi_info
import json

def get_matrix(tello_name, chessboardSize, size_of_chessboard_squares_mm, frameSize):
    img_location = f"telloImages_{tello_name}"

    ################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################


    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

    objp = objp * size_of_chessboard_squares_mm


    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    counter = 0

    print("Begin loading images")
    img_locationList = os.listdir(img_location)
    #if this breaks use glob
    for afile in img_locationList:
        if afile.endswith(".png"):
            if counter % 5 == 0:
                print(f"image {counter} of {len(os.listdir(img_location))} was loaded\n")
                img = cv2.imread(os.path.join(img_location, afile))
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, chessboardSize, None)
                # If found, add object points, image points (after refining them)
                if ret == True:
                    objpoints.append(objp)
                    corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                    imgpoints.append(corners)

            counter += 1


    ############## CALIBRATION #######################################################
    print("Begin camera calibration")
    ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints,
        frameSize, None, None)
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
