from typing import Optional, List, Tuple, Any
from server import Server
from datetime import datetime
from common.headings import *
import threading
import numpy as np
import os
import WP_Parser

import setup_path 
import airsim
import time

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
        host: str,
        port: Optional[int] = 22
    ) -> None:
        super().__init__(name, host, port=port)

        self.gps_period = gps_period
        self.takeoff_state: bool = False
        self.velocity: float = 0.
        self.position = np.zeros((3,))
        
        self.waypoint = None
        self.running_state : int = 0
        
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        
        self.client.takeoffAsync().join()
        """
        s = datetime.now()
        self.client.moveToPositionAsync(-100, -100,-100, 5)
        e = (datetime.now() - s).total_seconds()
        time.sleep(5)
        self.client.moveToPositionAsync(100, -100,-100, 5)
        
        print(e)
        """

        self.mean = mean
        self.sigma = sigma
        
    def start(self):
        super().start()

        conn, addr = self.socket.accept()
        elapsed = 0.
        running_state_print_interval = 5 #s
        timeout = 10
        run_state_start = datetime.now()
        timeout_start = datetime.now()

        with conn:
            print(f"Connected from {addr}")
            self.start_receiving(conn)

            while conn and self.running_state == 0:
                timeout_elapsed = (datetime.now() - timeout_start).total_seconds()
                if timeout_elapsed > timeout:
                    break
                
                start = datetime.now()
                encoded = self.get()
                if encoded:
                    data = self.protocol.decode(encoded)
                    
                    for name, value in data:

                        if name == TAKEOFF:
                            self.takeoff_state = True
                            print("Taking Off")

                        if name == LAND:
                            self.takeoff_state = False
                            self.landing()

                            print("Landing")

                        if name == RUNNING_STATE:
                            timeout_start = datetime.now()
                            new_start = datetime.now()
                            self.running_state = value
                            if (new_start - run_state_start).total_seconds() > running_state_print_interval:
                                print(f"Running state: {value}")
                                run_state_start = new_start
                                
                            if value == 0: pass # normal
                            elif value == 1:
                                print(f"Location Window Out {value}")
                                self.landing()
                                
                            elif value == 2: 
                                print(f"Time Window Out {value}")
                                self.landing()
                        
                        if name == DESIRED_VELOCITY:
                            print(f"Received desired velocity: {value}")
                            self.velocity = value
                            self.on_update()
                        
                        if name == NEXT_WAYPOINT:
                            print(f"Received Next Waypoint: {value}")
                            self.waypoint = self.protocol.decode_point(value)
                            self.on_update()

                step_elapsed = (datetime.now() - start).total_seconds()

                elapsed += step_elapsed
                if elapsed >= self.gps_period:
                    _position = self.client.simGetVehiclePose().position
                    self.position = np.array([_position.x_val, _position.y_val, _position.z_val])
                    print("--------", self.position)
                    
                    pos = self.position
                    #pos = self.randomize_gps(self.position)
                    pos = self.protocol.encode_point(pos)
                    byte_data = self.protocol.encode(pos, GPS_POSITION)
                    
                    if conn:
                        print("-------Sending GPS")
                        conn.sendall(byte_data)

                    elapsed = 0.
                    
            self.clean()
    
    def on_update(self):
        if self.waypoint is not None and self.velocity:
            print(f"Moving to {self.waypoint} with vel: {self.velocity}")
            self.client.moveToPositionAsync(*self.waypoint, self.velocity * 1.05)
            print(f"Moved to {self.waypoint} with vel: {self.velocity}")
    
    def randomize_gps(self, gps: np.ndarray) -> np.ndarray:
        return gps + np.random.normal(loc=self.mean, scale=self.sigma, size=(3,))

    def landing(self):
        print("Now Hovering")
        self.client.moveToPositionAsync(*self.position[:2], 1, 3).join()
        time.sleep(10)
        self.client.hoverAsync().join()
        print("Now Landing")
        self.client.landAsync().join()
        self.client.armDisarm(True)
        

def get_waypoints():
    home = os.path.expanduser('~')
    docs = os.path.join(home, "Documents")
    docs = os.path.join(docs, "AirSim")
    docs = os.path.join(docs, "WayPoints.txt")

    WPP = WP_Parser.WP_Data(docs, None)
    if WPP.IsFileOpen:

        con = 0
        waypoints = [[0,0,0],[0,0,-12]]
        while(1):

            new = WPP.ReadData(con, "WP")
            if new:
                con += 1

                waypoints.append([int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1])

            else:
                break

        new = WPP.ReadData(0, "WP")
        waypoints.append([int(new.Xoff), int(new.Yoff), int(new.Zoff)*-1])
        
        return np.array(waypoints)

    else:
        return None

if __name__ == "__main__":
    from common.headings import *
    import numpy as np
    from common.protocol import Protocol

    IP = "127.0.0.1"
    DRONE_PORT = 19875
    SERVER_PORT = 19876

    t_protocol = Protocol()

    #waypoints = get_waypoints()[:-1]
    waypoints = np.array([
        [0,0,0],
        [0,0,-12],
        [11, -6, -12],
        [23, -12, -12],
        [43, -12, -12],
        
    ])
    """
        [63, -12, -12],
        [83, -12, -12],
        [103, -12, -12],
        [113, -12, -12],
        [125, -12, -12],
        [125, -32, -12],
        [125, -52, -12],
        [125, -72, -12],
        [125, -92, -12],
        [125, -112, -12]
        """
    
    waypoints = t_protocol.encode_waypoints(waypoints)

    test_server = TestServer(
        "Center",
        [
            (WAYPOINTS, waypoints),
            (DESIRED_VELOCITY, 5.),
            (WINDOW_SIZE, 10.),
            (LOW_OFFSET, 0.9),
            (HIGH_OFFSET, 1.11),
            (COMMON_ERROR, 5.),
            (CHECK_PERIOD, 1.),
            (WAYPOINT_RANGE, 4.),
            (TAKEOFF, 1),
            (MISSION_START, 1)
        ],
        IP,
        SERVER_PORT,
        period=.3
    )
    drone = DroneServer(
        "Drone",
        .3,
        0,
        1,
        IP,
        DRONE_PORT
    )

    ts_thread = threading.Thread(target=test_server.start)
    drone_thread = threading.Thread(target=drone.start)

    ts_thread.start()
    drone_thread.start()
