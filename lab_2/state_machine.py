import time
import random
from XRPLib.defaults import *

def median(lst):
    lst = sorted(lst)
    n = len(lst)
    mid = n // 2
    if n % 2 == 0:
        return (lst[mid - 1] + lst[mid])/2
    else:
        return lst[mid]




class FSM:
    def __init__(self):
        self.state = 'start'
        # self.behaviors = {
        #     'start':      self.start,
        #     'random_walk': self.random_walk,
        #     'follow_wall': self.follow_wall
        # } # self.behaviors[self.state]()
        self.halt = False
        self.rangefinder_readings = []
    
    ################################
    ### behavior-based functions
    ### All must be momentary and
    ### non-blocking, as the control
    ### loop takes place in 
    ### self.monitor_states
    ################################

    def start(self):
        if board.is_button_pressed():
            print("switching from start to random_walk")
            self.state = 'random_walk'

    def random_walk(self):
        # default behavior: 
        straight = random.uniform(0, 1)
        turn = random.uniform(-1, 1)
        drivetrain.arcade(straight, turn)

        # state transfer behavior: 
        if rangefinder.distance() < 30:
            pass ## update state 

    ################################

    def follow_wall(self):
        raise NotImplementedError
    
    def follow_wall_straight(self):
        raise NotImplementedError
    
    def follow_wall_left(self):
        raise NotImplementedError
    
    def follow_wall_right(self):
        raise NotImplementedError
    
    ################################

    def follow_line(self):
        raise NotImplementedError
    
    def follow_line_straight(self):
        raise NotImplementedError
    
    def follow_line_left(self):
        raise NotImplementedError
    
    def follow_line_right(self):
        raise NotImplementedError

    ################################
    ### end behavior-based functions
    ################################

    ################################
    ### sensor-based functions
    ################################

    def median_distance(self):
        '''
        returns the median of the last n_to_mean rangefinder readings
        '''
        n_to_median = 5
        self.rangefinder_readings.append(rangefinder.distance())
        if len(self.rangefinder_readings) < n_to_median:
            return self.median_distance
            # If we haven't taken many readings yet,
            # this recursive call should keep sampling
            # until we have a list of at least n_to_median
            # and then return the median of that.
        if len(self.rangefinder_readings) > n_to_median:
            self.rangefinder_readings.pop(0)
        return median(self.rangefinder_readings)
    
    def reflectance_direction(self):
        reflectance.get_left()
        reflectance.get_right()
        raise NotImplementedError

    ################################
    ### end sensor-based functions
    ################################

    def monitor_states(self):
        while not self.halt:
            time.sleep(0.5)

            print('self.state is: ')
            print(getattr(self, 'state'))

            getattr(self, self.state)()
            # this line executes the function whose name 
            # is the current value of the self.state string

active_fsm = FSM()
active_fsm.monitor_states()