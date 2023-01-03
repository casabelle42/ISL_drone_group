
from djitellopy import tello
from datetime import datetime
import argparse
import pupil_apriltags as apriltags  # alias for apriltags
import cv2
import numpy as np #alias


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

def read_apriltags(frame, estimate_tag=False, camera_pars=None):
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

    detector = apriltags.Detector(families='tag36h11')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = detector.detect(gray, estimate_tag_pose=False, camera_params=None)
    return results

def adjust_drone(center_cam, center_gate):
    """function for adjusting drone ---- WORK IN PROGRESS

    Parameters
    ----------
    
    
    Returns
    -------
 

    """

    #if center_cam[0] == center_gate[1]:


def main(file_path, fps, width, height):
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

    # create the video writer
    FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, FOURCC, fps, (width, height), True)
    
    #connect to the tello
    tello_drone = tello.Tello()
    tello_drone.connect()
    battery = tello_drone.get_battery()

    print(f"Drone Battery: {battery}")

    tello_drone.takeoff()
    # hover

    tello_drone.streamon()  # camera on

    tello_drone.move_up(65)
    tello_drone.move_forward(30)

    while True:
        framerad = tello_drone.get_frame_read()
        img = framerad.frame
        results = read_apriltags(img)
        centerCAM = (int(width / 2), int(height / 2))

        if results:
            centers = get_apriltag_coords(results)
            img, box_center = find_box(centers, img)
            cv2.line(img, (int(box_center[0]), int(box_center[1])), centerCAM, (123, 255, 123), 2)
            cv2.circle(img, (int(box_center[0]), int(box_center[1])), 5, (255, 30, 12), -1)
        
        cv2.circle(img, centerCAM, 5, (20, 30, 12), -1)


        out.write(img)
        cv2.imshow("Image", img)
        keycode = cv2.waitKey(5)
        if (keycode & 0xFF) == ord('q'):
            #tello.land()
            break

    out.release()
    tello_drone.streamoff()

    tello_drone.land()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default=None, help='path to filename for video')
    parser.add_argument("--fps", type=int, default=30, help="frames per second for video")
    parser.add_argument("--width", type=int, default=960, help="width of camera image")
    parser.add_argument("--height", type=int, default=720, help="height of camera image")
    args = parser.parse_args()
    
    if args.filename is None:
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M")  # Format DateTime
        file_path = f"apriltag_detections_{dt_string}.mp4"  # added DateTime for TimeStamp
    else:
        file_path = args.filename
       
    main(file_path, args.fps, args.width, args.height)