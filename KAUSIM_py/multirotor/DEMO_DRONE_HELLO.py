import setup_path 
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2

import time


from ..Parser import WP_Parser

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

wind = airsim.Vector3r(0,-13,0)
# client.simSetWind(wind)




# airsim.wait_key('Press any key to takeoff')
client.takeoffAsync().join()
client.moveToPositionAsync(22, -10, -25, 5).join()
# state = client.getMultirotorState()
# print("state: %s" % pprint.pformat(state))
