#Tello Callibrator
import os
import cv2
from shutil import move
#constants
CHESSBOARD_SIZE = (8,10)
FRAME_SIZE = (960,720)
IMG_LOCATION = 'callibration_images'
DELETED_DIR = 'deleted_pics'
def main():
    # Arrays to store object points and image points from all the images.
    # UNUSED LISTS FOR NOW
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    #total img counter
    counter = 0
    #images with found chessboards counter
    ret_counter = 0
    #if deleted file path doesn't exist, create
    if not os.path.exists(DELETED_DIR):
        os.makedirs(DELETED_DIR)
    #establish dir length before modifying
    dir_length = len(os.listdir(IMG_LOCATION))
    #for file in dir list
    for file in os.listdir(IMG_LOCATION):
        if file.endswith(".png"):
            img = cv2.imread(f"{IMG_LOCATION}/{file}")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)
            #if chessboard found
            if ret:
                ret_counter +=1
                print(file + "- chessboard found")
            #if not found
            else:
                move(IMG_LOCATION+'/'+file, DELETED_DIR)
            #total counter increment
            counter += 1
            #print loading percent
            if counter % 5 == 0:
                print(f"loading : {int((counter/dir_length)*100)}%")
    #print total chessboards found
    print(str(ret_counter) + ' chessboards found.')

if __name__ == "__main__":
    main()
