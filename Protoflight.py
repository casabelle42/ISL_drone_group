from djitellopy import tello
import datetime
import pupil_apriltags as apriltags #alias for aprltags
import cv2

tello = tello.Tello()
tello.connect()
battery = tello.get_battery()

print(f"Drone Battery: {battery}")

tello.streamon()

tello.takeoff()



