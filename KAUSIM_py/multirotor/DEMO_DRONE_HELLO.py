import setup_path 
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2

import time


import WP_Parser

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

# wind = airsim.Vector3r(0,-13,0)
# client.simSetWind(wind)


client.takeoffAsync().join()
# client.moveToPositionAsync(22, -10, -25, 5).join()






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

            print(new.X)
            print(new.Y)
            print(new.Z)
            print(new.Xoff)
            print(new.Zoff)
            print(new.Yoff, "\n")

            client.moveToPositionAsync(int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1, 5).join()




        else:
            break

    new = WPP.ReadData(0, "WP")
    client.moveToPositionAsync(int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1, 5).join()
    
    client.hoverAsync().join()
    
    client.landAsync().join()

# client.armDisarm(False)
# client.enableApiControl(False)


# airsim.wait_key('Press any key to takeoff')

# client.takeoffAsync().join()
# client.moveToPositionAsync(22, -10, -25, 5).join()

# state = client.getMultirotorState()
# print("state: %s" % pprint.pformat(state))
