# test
'''
placeholder(what the program does)
'''
from djitellopy import tello
from datetime import datetime
import argparse
import cv2
import numpy as np  # alias
from wifi_tesing import 


def main(file_path):
    
    '''FPS = 30
    WIDTH = 960
    HEIGHT = 720'''
    TELLOIMAGES_DIR = 'telloImages'
    #FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
    #out = cv2.VideoWriter(file_path, FOURCC, FPS, (WIDTH, HEIGHT), True)
    tello_drone = tello.Tello()
    tello_drone.connect()
    battery = tello_drone.get_battery()
    
    print(f"Drone Battery: {battery}")

    tello_drone.streamon()  # camera on
    counter = 0
    
    while True:
        framerad = tello_drone.get_frame_read()
        img = framerad.frame
        results = read_apriltags(img)
        counter += 1
        if not os.path.exists(TELLOIMAGES_DIR):
        os.makedirs(TELLOIMAGES_DIR)
        
        imageFileName = os.path.join(TELLOIMAGES_DIR,f"image_caliberation{counter}.png")
        cv2.imwrite(imageFileName,img)
        cv2.imshow("Image", img)
        keycode = cv2.waitKey(5)
        if (keycode & 0xFF) == ord('q'):
            break

    #out.release()
    tello_drone.streamoff()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default=None)
    args = parser.parse_args()
    if args.filename is None:
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M")  # Format DateTime
        file_path = f"apriltag_detections_{dt_string}.mp4"  # added DateTime for TimeStamp
    else:
        file_path = args.filename
    print(file_path)
    main(file_path)
