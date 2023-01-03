import cv2
from djitellopy import Tello
import datetime
#HI

now = datetime.datetime.now().strftime('%Y%m%d_%H%M')

tello = Tello()
tello.connect()

tello.streamon()
frame_read = tello.get_frame_read()

tello.takeoff()
cv2.imwrite("picture_{}.png".format(now), frame_read.frame)
tello.streamoff()

tello.land()
tello.end()
