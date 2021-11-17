import numpy as np
from typing import List, Optional
from datetime import datetime

class LocationWindowManager:

    def __init__(
        self,
        desired_velocity: Optional[float] = None,
        window_size: Optional[float] = None,
        check_period: Optional[float] = None
    ):
        self.desired_velocity = desired_velocity
        self.window_size = window_size
        self.check_period = check_period
        self.check_time = None

    def in_range(
        self,
        current_position: np.ndarray,
        start_waypoint: np.ndarray,
        direction_vector: np.array,
        current_waypoint: np.ndarray
    ) -> bool:
        """
        주기마다 실행
        """
        
        if self.check_time:
            distance_to_current_wp = np.linalg.norm(current_waypoint - current_position)
            
            print(f"Start Point: {start_waypoint}")
            temp = (datetime.now() - self.check_time).total_seconds() - 2
            elapsed_time = temp if temp > 0 else 0
            print(f"DirVec: {direction_vector} DesVel: {self.desired_velocity} t: {elapsed_time}")
            
            E_travel_distance = elapsed_time * self.desired_velocity
            E_location = start_waypoint + (direction_vector * E_travel_distance)
            print(f"Checking Location-Des: {E_location}, Real: {current_position}")
            diff = np.linalg.norm(current_position - E_location)
            diff = distance_to_current_wp if diff > distance_to_current_wp else diff
            print(diff)
            return diff <= self.window_size
        else:
            return True
    
    def record_time(self):
        self.check_time = datetime.now()


class TimeWindowManager:

    def __init__(
        self,
        desired_velocity: Optional[float] = None,
        low_offset: Optional[float] = None,
        high_offset: Optional[float] = None,
        common_error: Optional[float] = None
    ):
        self.desired_velocity = desired_velocity
        self.low_offset = low_offset
        self.high_offset = high_offset
        self.common_error = common_error
        
        self.last_check_time = None

    def in_range(
        self,
        current_pos: np.ndarray,
        last_waypoint: np.ndarray
    ) -> bool:
        """
        waypoint 도달마다 실행
        기대 경과 시간
        """
        
        if self.last_check_time:
            elapsed_time = (datetime.now() - self.last_check_time).total_seconds()
            
            #print(f"LastW: {last_waypoint} CurrPos: {current_pos}")
            
            d = abs(np.linalg.norm(last_waypoint - current_pos))
            E_time = d/self.desired_velocity
            low = E_time * self.low_offset - self.common_error
            high = E_time * self.high_offset + self.common_error
            
            #print(f"Checking Time-Des: {low}~{E_time}~{high}, Real: {elapsed_time}")
            self.last_check_time = datetime.now()

            return low <= elapsed_time <= high
        
        else: # init
            self.last_check_time = datetime.now()
            return True

    def update_check_time(self):
        self.last_check_time = datetime.now()
