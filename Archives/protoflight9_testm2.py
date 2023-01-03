# test
from djitellopy import tello
from datetime import datetime
import pupil_apriltags as apriltags  # alias for aprltags
import cv2

def display_movement(imgContour, deadZone, height, width, direction):
        cv2.putText(imgContour, direction, (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        cv2.rectangle(imgContour, (0, int(height / 2 - deadZone)),
                (int(width / 2) - deadZone, int(height / 2) + deadZone), (0, 0, 255), cv2.FILLED)
        return imgContour

def display_grid(img, deadZone, width, height):
    print(f'deadZone {DEADZONE}')
    cv2.line(img, (int(width / 2) - deadZone, 0), (int(width / 2) - deadZone, height), (255, 255, 0), 3)
    cv2.line(img, (int(width / 2) + deadZone, 0), (int(width / 2) + deadZone, height), (255, 255, 0), 3)
    cv2.circle(img, (int(width / 2), int(height / 2)), 5, (0, 0, 255), 5) 
    cv2.line(img, (0, int(height / 2) - deadZone), (width, int(height / 2) - deadZone), (255, 255, 0), 3)
    cv2.line(img, (0, int(height / 2) + deadZone), (width, int(height / 2) + deadZone), (255, 255, 0), 3)
    return img


now = datetime.now()  # Get DateTime
dt_string = now.strftime("%Y%m%d_%H%M")  # Format DateTime

detector = apriltags.Detector(families='tag36h11')

FILE_PATH = f"apriltag_detections_{dt_string}.mp4"  # added DateTime for TimeStamp
FPS = 30
WIDTH = 960
HEIGHT = 720
DEADZONE = 100
FOURCC = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(FILE_PATH, FOURCC, FPS, (WIDTH, HEIGHT), True)
centerx = 0
centery = 0

tello = tello.Tello()
tello.connect()
battery = tello.get_battery()

print(f"Drone Battery: {battery}")

tello.takeoff()
# hover

tello.streamon()  # camera on

tello.move_up(65)
tello.move_forward(30)

while True:
    framerad = tello.get_frame_read()
    img = framerad.frame
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    results = detector.detect(gray, estimate_tag_pose=False, camera_params=None)
    '''while results < 2:
        if results == 1:
            tello.move_back(20)
        else:
            tello.rotate_clockwise(20)
            #find out up and down movement
    while(results >= 2) and (results <= 3):
        tello.move_back(30)'''
    print(f"[INFO] {len(results)} total AprilTags detected")

    xcords = []
    ycords = []

    if results:
        for r in results:
            tagFamily = r.tag_family.decode("utf-8")
            tagID = r.tag_id
            tagIDstring = f"tagID{tagID}"
            # extract the bounding box (x, y)-coordinates for the AprilTag
            # and convert each of the (x, y)-coordinate pairs to integers
            (ptA, ptB, ptC, ptD) = r.corners
            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))
            ptA = (int(ptA[0]), int(ptA[1]))

            # draw the bounding box of the AprilTag detection
            cv2.line(img, ptA, ptB, (0, 255, 0), 2)
            cv2.line(img, ptB, ptC, (0, 255, 0), 2)
            cv2.line(img, ptC, ptD, (0, 255, 0), 2)
            cv2.line(img, ptD, ptA, (0, 255, 0), 2)

            # draw the center (x, y)-coordinates of the AprilTag
            cX, cY = (int(r.center[0]), int(r.center[1]))
            cv2.circle(img, (cX, cY), 5, (0, 0, 255), -1)

            # list with centers of apriltags

            xcords.append(cX)
            ycords.append(cY)
    # Print X, and Y coords being seen by the drone
    print(f"Xcords{xcords}")
    print(f"Ycords{ycords}")

    print(len(xcords))
    centerCAM = (int(WIDTH / 2), int(HEIGHT / 2))
    if xcords:
        # Max/Min of x-cordinates & y-cordinates:::
        x_max = max(xcords)
        print(f"Xmax{x_max}")
        x_min = min(xcords)
        print(f"x_min{x_min}")
        y_max = max(ycords)
        print(f"y_max{y_max}")
        y_min = min(ycords)
        print(f"y_min{y_min}")

        centery = (y_max + y_min) / 2
        centerx = (x_max + x_min) / 2
        print(f"centerYcords{centery}")
        print(f"centerXcords{centerx}")

    

        #cv2.line(img, (int(centerx), int(centery)), centerCAM, (123, 255, 123), 2)

 
    cv2.circle(img, (int(centerx), int(centery)), 5, (255, 30, 12), -1)
    cv2.circle(img, centerCAM, 5, (20, 30, 12), -1)



    if (centerx < int(WIDTH / 2) - DEADZONE):
        img = display_movement(img, DEADZONE, HEIGHT, WIDTH, "GO LEFT")
        dir = 1
        tello.yaw_velocity = -60

    elif (centerx > int(WIDTH / 2) + DEADZONE):
        img = display_movement(img, DEADZONE, HEIGHT, WIDTH, "GO RIGHT")
        dir = 2
        tello.yaw_velocity = 60

    elif (centery < int(HEIGHT / 2) - DEADZONE):
        img = display_movement(img, DEADZONE, HEIGHT, WIDTH, "GO UP")
        dir = 3
        tello.up_down_velocity = 60

    elif (centery > int(HEIGHT / 2) - DEADZONE):
        img = display_movement(img, DEADZONE, HEIGHT, WIDTH, "GO DOWN")
        dir = 4
        tello.up_down_velocity = -60
        

    
    
    grid = display_grid(img, DEADZONE, WIDTH, HEIGHT)
    out.write(grid)
    cv2.imshow("Image", grid)
    keycode = cv2.waitKey(5)
    if (keycode & 0xFF) == ord('q'):
        #tello.land()
        break

out.release()
tello.streamoff()

tello.land()
cv2.destroyAllWindows()
