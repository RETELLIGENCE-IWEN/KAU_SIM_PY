import setup_path 
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2

import time

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)



# state = client.getMultirotorState()
# s = pprint.pformat(state)
# print("state: %s" % s)

# imu_data = client.getImuData()
# s = pprint.pformat(imu_data)
# print("imu_data: %s" % s)

# barometer_data = client.getBarometerData()
# s = pprint.pformat(barometer_data)
# print("barometer_data: %s" % s)

# magnetometer_data = client.getMagnetometerData()
# s = pprint.pformat(magnetometer_data)
# print("magnetometer_data: %s" % s)

# gps_data = client.getGpsData()
# s = pprint.pformat(gps_data)
# print("gps_data: %s" % s)

# airsim.wait_key('Press any key to takeoff')
client.takeoffAsync().join()
client.moveToPositionAsync(0, 0, -30, 5).join()
# state = client.getMultirotorState()
# print("state: %s" % pprint.pformat(state))

# airsim.wait_key('Press any key to move vehicle to (-10, 10, -10) at 5 m/s')




client.moveToPositionAsync(-26, 0, -30, 2).join()

client.hoverAsync().join()

state = client.getMultirotorState()
# print("state: %s" % pprint.pformat(state))

# airsim.wait_key('Press any key to take images')
# get camera images from the car
responses = client.simGetImages([
    airsim.ImageRequest("0", airsim.ImageType.DepthVis),  #depth visualization image
    airsim.ImageRequest("1", airsim.ImageType.DepthPerspective, True), #depth in perspective projection
    airsim.ImageRequest("1", airsim.ImageType.Scene), #scene vision image in png format
    airsim.ImageRequest("1", airsim.ImageType.Scene, False, False)])  #scene vision image in uncompressed RGBA array
print('Retrieved images: %d' % len(responses))

# tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_drone")

tmp_dir = os.path.join("D:\KAU_SIM_2021", "imagesTaken")


print ("Saving images to %s" % tmp_dir)
# try:
#     os.makedirs(tmp_dir)
# except OSError:
#     if not os.path.isdir(tmp_dir):
#         raise

# for response in responses:
#     img_rgb_1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) 
#     img_rgb = img_rgb_1d.reshape(response.height, response.width, 3)
#     # for saving, you can do :
#     cv2.imwrite(time.strftime("%Y%m%d-%H%M%S") + ".png", img_rgb)


for idx, response in enumerate(responses):
    
    filename = os.path.join(tmp_dir, str(idx))

    if response.pixels_as_float:
        print("Type %d, size %d" % (response.image_type, len(response.image_data_float)))
        airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
    elif response.compress: #png format
        print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
        airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)
    else: #uncompressed array
        print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
        img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 4 channel image array H X W X 3
        cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # write to png



# 제 1 사거리
client.moveToPositionAsync(-26, -90, -30, 2).join()
# time.sleep(3)

client.rotateByYawRateAsync(-45, 2).join()


# 골목길 1
client.moveToPositionAsync(-60, -90, -30, 2).join()

client.rotateByYawRateAsync(-45, 2).join()
client.rotateByYawRateAsync(-45, 2).join()


# 제 1 사거리
client.moveToPositionAsync(-26, -90, -30, 2).join()
client.rotateByYawRateAsync(-45, 2).join()

# 제 2 사거리
client.moveToPositionAsync(-26, -125, -30, 2).join()


client.rotateByYawRateAsync(-45, 2).join()
client.rotateByYawRateAsync(-45, 2).join()


# 제 1 사거리
client.moveToPositionAsync(-26, -90, -30, 2).join()






client.hoverAsync().join()
time.sleep(10)




# client.armDisarm(False)


# that's enough fun for now. let's quit cleanly

time.sleep(10)
client.enableApiControl(False)
