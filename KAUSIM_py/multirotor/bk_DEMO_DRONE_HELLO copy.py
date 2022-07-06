import setup_path 
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2

import time


import WP_Parser


# m/s
desired_speed  = 5







# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)




SetWind = 0
SetCollision = False

# 12 mph
# wind = airsim.Vector3r(-8.5,-8.5,0)

# 17 mph
# wind = airsim.Vector3r(-12,-12,0)
wind = airsim.Vector3r(17,0,0)

# 21.2 mph
# wind = airsim.Vector3r(-15,-15,0)

# 24 mph
# wind = airsim.Vector3r(0,-17,0)

if SetWind : client.simSetWind(wind)




client.takeoffAsync().join()
# client.moveToPositionAsync(22, -10, -25, 5).join()


way_points = []



home = os.path.expanduser('~')
docs = os.path.join(home, "Documents")
docs = os.path.join(docs, "AirSim")
docs = os.path.join(docs, "WayPoints.txt")
print(docs)

WPP = WP_Parser.WP_Data(docs, None)
if WPP.IsFileOpen:

    con = 0
    while(1):

        new = WPP.ReadData(con, "WP")
        if new:
            con += 1

            print("Proceeding to Waypoint [", con, "]")
            # print(new.X)
            # print(new.Y)
            # print(new.Z)
            print(" - X : ", new.Xoff)
            print(" - Y : ", new.Yoff)
            print(" - Z : ", new.Zoff, "\n")

            client.moveToPositionAsync(int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1, 5).join()


            #simulate collision via exteame wind
            if con == 2:

                wind = airsim.Vector3r(-100,-100,0)
                if SetCollision : client.simSetWind(wind)




        else:
            break

    new = WPP.ReadData(0, "WP")
    print("Proceeding to StartingPoint")
    client.moveToPositionAsync(int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1, 5).join()
    
    client.hoverAsync().join()
    
    print("Landing")
    client.landAsync().join()

# client.armDisarm(False)
# client.enableApiControl(False)


# airsim.wait_key('Press any key to takeoff')

# client.takeoffAsync().join()
# client.moveToPositionAsync(22, -10, -25, 5).join()

# state = client.getMultirotorState()
# print("state: %s" % pprint.pformat(state))
