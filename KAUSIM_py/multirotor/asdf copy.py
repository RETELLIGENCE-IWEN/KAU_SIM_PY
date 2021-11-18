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

class EnvServer(Server):

    def __init__(
        self,
        name: str,
        client,
        host: str,
        port: Optional[int] = 22,
        period: Optional[float] = 1.,
    ) -> None:
        super().__init__(name, host, port=port)
        self.client = client
        self.period = period

    def start(self):
        super().start()
        conn, addr = self.socket.accept()
        timeout = 5
        timeout_start = datetime.now()
        

        with conn:
            print(f"Connected from {addr}")
            self.start_receiving(conn)
            print(f"{self.name} {self.running}")

            while self.running:
                timeout_elapsed = (datetime.now() - timeout_start).total_seconds()
                if timeout_elapsed > timeout and self.takeoff_state:
                    print(f"{name} timeout from no input")
                    break
                
                encoded = self.get()
                if encoded:
                    data = self.protocol.decode(encoded)
                    
                    for name, value in data:
                        if name == Desired_Wind:
                            decoded = self.parse_wind(value)
                            print(f"Setting wind to {decoded}")
                            wind = airsim.Vector3r(*decoded)
                            self.client.simSetWind(wind)
                        
                        if name == Desired_Error_Strength:
                            print(f"Setting error strength to {value}")
                            self.sigma = value
                            
            print(f"{self.name} {self.running}")
            self.clean()

    def parse_wind(self, value: str) -> np.ndarray:
        # remove ()
        stripped = value[1:-1]
        splitted = stripped.split(",")
        in_list = list(map(lambda x: float(x), splitted))
        return np.array(in_list)
    
class DroneServer(Server):

    def __init__(
        self,
        name,
        gps_period: float,
        mean: float,
        sigma: float,
        client,
        host: str,
        port: Optional[int] = 22,        
    ) -> None:
        super().__init__(name, host, port=port)

        self.gps_period = gps_period
        self.takeoff_state: bool = False
        self.velocity: float = 0.
        self.position = np.zeros((3,))
        
        self.waypoint = None
        self.running_state : int = 0
        self.client = client        

        self.mean = mean
        self.sigma = sigma
        
    def start(self):
        super().start()

        conn1, addr = self.socket.accept()
        conn2, addr = self.socket.accept()
        
        running_state_print_interval = 5 #s
        elapsed = 0.
        run_state_start = datetime.now()
        timeout = 5
        timeout_start = datetime.now()

        with conn1:
            print(f"Connected from {addr}")
            self.start_receiving(conn1)
            self.start_receiving(conn2)

            while conn1 and self.running_state == 0:
                timeout_elapsed = (datetime.now() - timeout_start).total_seconds()
                if timeout_elapsed > timeout and self.takeoff_state:
                    print(f"GPS Time OUT from no running state")
                    break
                
                start = datetime.now()
                encoded = self.get()
                if encoded:
                    data = self.protocol.decode(encoded)
                    
                    for name, value in data:

                        # This should be moved to other places
                        if name == Desired_Wind:
                            decoded = self.protocol.decode_point(value)
                            print(f"Setting wind to {decoded}")
                            wind = airsim.Vector3r(*decoded)
                            self.client.simSetWind(wind)
                        
                        # This also should be moved to other places
                        if name == Desired_Error_Strength:
                            print(f"Setting error strength to {value}")
                            self.sigma = value

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
                    #print("--------", self.position)
                    
                    pos = self.randomize_gps(self.position)
                    pos = self.protocol.encode_point(pos)
                    byte_data = self.protocol.encode(pos, GPS_POSITION)
                    
                    if conn1:
                        #print("-------Sending GPS")
                        conn1.sendall(byte_data)

                    elapsed = 0.
                    
            self.clean()
    
    def on_update(self):
        if self.waypoint is not None and self.velocity:
            print(f"Moving to {self.waypoint} with vel: {self.velocity}")
            self.client.moveToPositionAsync(*self.waypoint, self.velocity * 1.02)
            #print(f"Moved to {self.waypoint} with vel: {self.velocity}")
    
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
    ENV_PORT = 19877

    
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)

    t_protocol = Protocol()
    """
    env_server = EnvServer(
        "Env Server",
        client,
        IP,
        ENV_PORT
    )
    env_thread = threading.Thread(target=env_server.start)
    env_thread.start()
    
    not_ready = ""
    while not_ready != "ready":
        not_ready = input("When connection is set, enter ready: ")
    """
        
    client.takeoffAsync().join() # Start ENV before takeoff
    
    #waypoints = get_waypoints()[:-1]
    waypoints = np.array([
        [0,0,0],
        [0,0,-12],
        [11, -6, -12],
        [23, -12, -12],
        [43, -12, -12],
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
    ])
    
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
        client,
        IP,
        DRONE_PORT
    )

    ts_thread = threading.Thread(target=test_server.start)
    drone_thread = threading.Thread(target=drone.start)

    drone_thread.start()
    
    ts_thread.start()
