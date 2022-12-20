# test
'''
placeholder(what the program does)
'''
from djitellopy import tello
from datetime import datetime
import os
import argparse
import cv2
import numpy as np  # alias
from wifi_testing import get_wifi_info
from tello_remove_bad import remove_bad_images
from tello_calibration import get_matrix 


def main(chessboard_size, frame_size, chessboard_square_size):

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
