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
import tello_callibration


def main():
    #added tello_name 
    TELLO_NAME = get_wifi_info()
    TELLOIMAGES_DIR = f"telloImages_{TELLO_NAME}"
    if not os.path.exists(TELLOIMAGES_DIR):
        os.makedirs(TELLOIMAGES_DIR)
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
            imageFileName = os.path.join(TELLOIMAGES_DIR,f"{TELLO_NAME}{datetime.now()}.png")
            cv2.imwrite(imageFileName,img)
            cv2.imshow("Image", img)
        keycode = cv2.waitKey(5)
        if (keycode & 0xFF) == ord('q'):
            break
        elif counter == 500:
            break
    tello_drone.streamoff()
    cv2.destroyAllWindows()
    remove_bad_images()
    tello_callibration()
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default=None, type=str)
    parser.add_argument("--fps", default=30, type=int)
    parser.add_argument("--width", default=960, type=int)
    parser.add_argument("--height", default=720, type=int)
    args = parser.parse_args()
    if args.filename is None:
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M")  # Format DateTime
    else:
        file_path = args.filename
    main()
