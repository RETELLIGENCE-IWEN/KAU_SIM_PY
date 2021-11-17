from typing import Optional, List, Tuple, Any
from server import Server
from datetime import datetime
from common.headings import *
import threading
import numpy as np

import setup_path 
import airsim

import os
import tempfile
import pprint
import cv2

import time


import WP_Parser


class TestServer(Server):

    def __init__(
        self,
        name: str,
        data: List[Tuple[str, Any]],
        host: str,
        port: Optional[int] = 22,
        period: Optional[float] = 1.,
    ) -> None:
        super().__init__(name, host, port=port)

        self.period = period
        self.data = data

    def start(self):
        super().start()
        conn, addr = self.socket.accept()
        elapsed = 0.

        with conn:
            print(f"Connected from {addr}")
            self.start_receiving(conn)

            while self.data and conn:
                start = datetime.now()

                elapsed += (datetime.now() - start).total_seconds()

                if elapsed >= self.period:
                    data = self.data.pop(0)
                    print(f"Server sending : {data[0]}")
                    byte_data = self.protocol.encode(data[1], data[0])
                    conn.sendall(byte_data)

                    elapsed = 0.

            self.clean()


class DroneServer(Server):

    def __init__(
        self,
        name,
        gps_period: float,
        mean: float,
        sigma: float,
        client,
        _wayPoints, 
        host: str,
        port: Optional[int] = 22,
    ) -> None:
        super().__init__(name, host, port=port)

        self.gps_period = gps_period
        self.takeoff_state: bool = False
        self.velocity: float = 0.
        self.direction: np.ndarray = np.zeros((3,))
        self._wayPoints = _wayPoints
        self.position = np.zeros((3,))
        self.client = client

        self.mean = mean
        self.sigma = sigma
        conn, addr = self.socket.accept()
        self.conn = conn
        self.addr = addr



    def start(self):
        super().start()


        conn = self.conn
        addr = self.addr
        
        elapsed = 0.

        with conn:
            print(f"Connected from {addr}")
            self.start_receiving(conn)

            while conn:
                start = datetime.now()
                encoded = self.get()
                if encoded:
                    data = self.protocol.decode(encoded)

                    for name, value in data:

                        if name == TAKEOFF:
                            self.takeoff_state = True
                            print("Taking Off")
                            self.client.takeoffAsync().join()

                        if name == LAND:
                            self.takeoff_state = False
                            self.client.landAsync().join()

                            print("Landing")

                        if name == RUNNING_STATE:
                            print(f"Running state: {value}")
                            if value == 0: pass # normal
                            elif value == 1:
                                print(f"Time Out")
                                self.client.landAsync().join()
                            elif value == 2: 
                                print(f"Location Out")
                                self.client.landAsync().join()



                step_elapsed = (datetime.now() - start).total_seconds()

                elapsed += step_elapsed
                if elapsed >= self.gps_period:

                    # get gps data
                    # save as self position
                    # self.position = self.client.getMultirotorState().position
                    print("--------Retracting Position From Simulator")
                    _position = self.client.simGetVehiclePose().position
                    self.position = np.array([_position.x_val, _position.y_val, _position.z_val*-1])
                    print("--------", self.position)
                    print("--------", _position.x_val, _position.y_val, _position.z_val)
                    # print("x={}, y={}, z={}".format(pose.position.x_val, pose.position.y_val, pose.position.z_val))
                    pos = self.randomize_gps(self.position)
                    pos = self.protocol.encode_point(pos)
                    byte_data = self.protocol.encode(pos, GPS_POSITION)
                    
                    if conn:
                        print("-------Sending GPS")
                        conn.sendall(byte_data)

                    elapsed = 0.

            self.clean()

    def move(self, time: float):

        
        # self.position += self.direction * self.velocity * time
        temporary_velocity = self.direction * self.velocity
        self.client.moveByVelocityAsync(*temporary_velocity, time)

    def randomize_gps(self, gps: np.ndarray) -> np.ndarray:
        return gps + np.random.normal(loc=self.mean, scale=self.sigma, size=(3,))



def spacer():
    pass

def Automatic_DroneControl(_client, wayPoints, _velocity, _parent):
    for index in range(len(wayPoints)):


        print("Action Move To Please", index)
        _client.moveToPositionAsync(wayPoints[index][0], wayPoints[index][1], wayPoints[index][2], _velocity).join()
        Event_WayPoint_Arrival(_parent)

    _client.hoverAsync().join()

    _client.landAsync().join()


def Event_WayPoint_Arrival(_papa):

    print("Event : Way-Point Arrival")
    data = _papa.protocol.encode(0, WAYPOINT_REACHED)
    _papa.conn.send(data)








if __name__ == "__main__":
    from common.headings import *
    import numpy as np
    from common.protocol import Protocol

    IP = "127.0.0.1"
    DRONE = 19875
    CENTER = 19876

    t_protocol = Protocol()


    way_points = []


    # connect to the AirSim simulator
    T_client = airsim.MultirotorClient()
    T_client.confirmConnection()
    T_client.enableApiControl(True)
    T_client.armDisarm(True)

    # wind = airsim.Vector3r(-1,0,0)
    # client.simSetWind(wind)







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

                way_points.append([int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1])



            else:
                break

        new = WPP.ReadData(0, "WP")
        way_points.append([int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1])

    #    self.client.moveToPositionAsync(int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1, 5).join()
    waypoints = np.array(way_points)



    waypoints = t_protocol.encode_waypoints(waypoints)

    test_server = TestServer(
        "Center",
        [
            (WAYPOINTS, waypoints),
            (DESIRED_VELOCITY, 5.),
            (WINDOW_SIZE, 10.),
            (LOW_OFFSET, 5.),
            (HIGH_OFFSET, 5.),
            (COMMON_ERROR, 1.),
            (CHECK_PERIOD, 1.),
            (WAYPOINT_RANGE, 5.),
            (TAKEOFF, 1),
            (MISSION_START, 1)
        ],
        IP,
        CENTER,
        period=.3
    )
    drone = DroneServer(
        "Drone",
        1,
        0,
        1,
        T_client,
        way_points,
        IP,
        DRONE
    )



    ts_thread = threading.Thread(target=test_server.start)
    drone_thread = threading.Thread(target=drone.start)
    automtion_thread = threading.Thread(target=Automatic_DroneControl, args=(T_client, way_points, 5, drone))



    ts_thread.start()
    drone_thread.start()
    automtion_thread.start()
