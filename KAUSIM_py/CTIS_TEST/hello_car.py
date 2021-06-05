import setup_path
import airsim
import cv2
import numpy as np
import os
import sys
import time
import tempfile

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# import setup_path_CITS
import CITS_Server

# Connect to CITS
my = CITS_Server.CITS_SERVER()

# connect to the AirSim simulator
client = airsim.CarClient()
client.confirmConnection()
client.enableApiControl(True)
print("API Control enabled: %s" % client.isApiControlEnabled())
car_controls = airsim.CarControls()

tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_car")
print ("Saving images to %s" % tmp_dir)
try:
    os.makedirs(tmp_dir)
except OSError:
    if not os.path.isdir(tmp_dir):
        raise


# get state of the car
car_state = client.getCarState()
print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

# get state of car CITS
my.CITS_Request(0, 0)
my.CITS_Request(1, 0)
my.CITS_Request(2, 0)
my.CITS_Request(3, 0)
my.CITS_Request(4, 0)

# go forward 1
car_controls.throttle = 0.5
car_controls.steering = 0
client.setCarControls(car_controls)
print("Go Forward")
time.sleep(5)   # let car drive a bit

# get state of car CITS
my.CITS_Request(0, 0)
my.CITS_Request(1, 0)
my.CITS_Request(2, 0)
my.CITS_Request(3, 0)
my.CITS_Request(4, 0)

# Go forward + steer left 2
car_controls.throttle = 0.5
car_controls.steering = -0.5
client.setCarControls(car_controls)
print("Go Forward, steer right")
time.sleep(3)   # let car drive a bit

# get state of car CITS
my.CITS_Request(0, 0)
my.CITS_Request(1, 0)
my.CITS_Request(2, 0)
my.CITS_Request(3, 0)
my.CITS_Request(4, 0)

# go forward 3
car_controls.throttle = 0.5
car_controls.steering = 0
client.setCarControls(car_controls)
print("Go Forward")
time.sleep(1)   # let car drive a bit

# get state of car CITS
my.CITS_Request(0, 0)
my.CITS_Request(1, 0)
my.CITS_Request(2, 0)
my.CITS_Request(3, 0)
my.CITS_Request(4, 0)

# apply brakes 4
car_controls.brake = 1
client.setCarControls(car_controls)
print("Apply brakes")
time.sleep(3)   # let car drive a bit
car_controls.brake = 0 #remove brake

# get state of the car
car_state = client.getCarState()
print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

# get state of car CITS
my.CITS_Request(0, 0)
my.CITS_Request(1, 0)
my.CITS_Request(2, 0)
my.CITS_Request(3, 0)
my.CITS_Request(4, 0)

# go forward + go right 5
car_controls.throttle = 0.5
car_controls.steering = 0.4
client.setCarControls(car_controls)
print("Go Forward")
time.sleep(4.15)   # let car drive a bit

# apply brakes 6
car_controls.brake = 1
client.setCarControls(car_controls)
print("Apply brakes")
time.sleep(3)   # let car drive a bit
car_controls.brake = 0 #remove brake

# get state of car CITS
my.CITS_Request(0, 0)
my.CITS_Request(1, 0)
my.CITS_Request(2, 0)
my.CITS_Request(3, 0)
my.CITS_Request(4, 0)

# go forward 7
car_controls.throttle = 1
car_controls.steering = 0
client.setCarControls(car_controls)
print("Go Forward")
time.sleep(3.5)   # let car drive a bit

# apply brakes 8
car_controls.brake = 1
client.setCarControls(car_controls)
print("Apply brakes")
time.sleep(3)   # let car drive a bit
car_controls.brake = 0 #remove brake









client.enableApiControl(False)
