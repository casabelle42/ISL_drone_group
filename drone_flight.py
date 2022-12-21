import os.path

from djitellopy import tello
from datetime import datetime
from wifi_testing import get_wifi_info
import argparse
import pupil_apriltags as apriltags  # alias for apriltags
import cv2
import numpy as np #alias'
import time
import json



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

def find_box(a_tag_centers, img):
    """function that will draw a box and midpoint of the box with given april tag list
    Parameters
    ----------
    a_tag_centers: list 
        list of centers of apriltags
    
    img : image
        image to be manipulated
    
    Returns
    -------
    img : image
        image that was manipulated
    center : tuple
        center of the apriltag array
    """  
    
    center_array = np.array(a_tag_centers)
    pt_a = int(min(center_array[:, 0])), int(max(center_array[:, 1]))
    pt_b = int(min(center_array[:, 0])), int(min(center_array[:, 1]))
    pt_c = int(max(center_array[:, 0])), int(min(center_array[:, 1]))
    pt_d = int(max(center_array[:, 0])), int(max(center_array[:, 1]))
    center_x = int((max(center_array[:, 0]) + min(center_array[:, 0]))/2)
    center_y = int((max(center_array[:, 1]) + min(center_array[:, 1]))/2)
    center = (center_x, center_y)
    cv2.line(img, pt_a, pt_b, (255, 0, 0), 4)
    cv2.line(img, pt_b, pt_c, (255, 0, 0), 4)
    cv2.line(img, pt_c, pt_d, (255, 0, 0), 4)
    cv2.line(img, pt_d, pt_a, (255, 0, 0), 4)
    return img, center

def read_apriltags(frame, camera_matrix):
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
        camera_pars = [camera_matrix['fx'],camera_matrix['fy'],camera_matrix['cx'],camera_matrix['cy']]
        detector = apriltags.Detector(families='tag36h11')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = detector.detect(gray, estimate_tag_pose=estimate_tag, camera_params=camera_pars, tag_size=.025)
    return results

def get_direction(cx, cy, img, frameWidth, frameHeight, deadZone, dir):
    if (cx <int(frameWidth/2)-deadZone):
        cv2.putText(img, " GO LEFT " , (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
        dir = 1
    elif (cx > int(frameWidth / 2) + deadZone):
        cv2.putText(img, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
        dir = 2
    elif (cy < int(frameHeight / 2) - deadZone):
        cv2.putText(img, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
        dir = 3
    elif (cy > int(frameHeight / 2) + deadZone):
        cv2.putText(img, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
        dir = 4
    return dir




def main(file_path, fps, width, height, tello_name):
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
        
    Returns
    -------
    None
    """  
    #CONSTANTS
    DEADZONE = 100
    #Variables
    json_path = f"camera_matrix_{tello_name}.json"
    if os.path.exists(json_path):
        with open(json_path) as f:
            camera_matrix = json.load(f)
    else:
        camera_matrix = {}
    # create the video writer
    FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, FOURCC, fps, (width, height), True)
    
    #Counter
    testDrone = False   #False for flight, True for testing (flight disabled)

    #connect to the tello
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
        results = read_apriltags(img,camera_matrix)
        centerCAM = (int(width / 2), int(height / 2))

        # SEND VELOCITY VALUES TO TELLO
        direction = 0
        if results:
            centers = get_apriltag_coords(results)
            img, box_center = find_box(centers, img)
            centerX = int(box_center[0])
            centerY = int(box_center[1])
            cv2.line(img, (centerX, centerY), centerCAM, (123, 255, 123), 2)
            cv2.circle(img, (centerX, centerY), 5, (255, 30, 12), -1)
            direction = get_direction(centerX, centerY, img, width, height, DEADZONE, direction)
            print(f"frame {frame_counter}")
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
            drone.send_rc_control(drone.left_right_velocity, drone.for_back_velocity, drone.up_down_velocity, drone.yaw_velocity)
        print(dir)

        
        cv2.circle(img, centerCAM, 5, (20, 30, 12), -1)
        #if drone is centered change gate square from blue to green

        out.write(img)
        cv2.imshow("Image", img)
        keycode = cv2.waitKey(5)
        if (keycode & 0xFF) == ord('q'):
            #tello.land()
            break

    out.release()
    drone.streamoff()

    drone.land()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    tello_name = get_wifi_info()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default=None, help='path to filename for video')
    parser.add_argument("--fps", type=int, default=30, help="frames per second for video")
    parser.add_argument("--width", type=int, default=960, help="width of camera image")
    parser.add_argument("--height", type=int, default=720, help="height of camera image")
    args = parser.parse_args()

    if args.filename is None:
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M")  # Format DateTime
        file_path = f"{tello_name}_apriltag_detections_{dt_string}.mp4"  # added DateTime for TimeStamp
    else:
        file_path = args.filename
       
    main(file_path, args.fps, args.width, args.height, tello_name)
                      
                      
