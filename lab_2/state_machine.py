import time
import random
import akmath
from XRPLib.defaults import *

class LineWallFSM:
    def __init__(self):
        self.state = 'start'
        self.halt = False
        self.rangefinder_readings = []

        self.target_wall_dist = 15 # [cm]
        self.verbosity = ('general', 'on_state_switch', 'follow_line_debug', 'follow_wall_debug') # options: 'general', 'on_state_switch', 'reflectance_debug', 'follow_wall_debug'

        # reflectance:
        r_tile = 0.7704468
        r_tape = 0.7367401
        # self.reflectance_mapping's output is a DifferentialDrive.arcade turn value, where
        # +1 is left and -1 is right
        self.reflectance_mapping = akmath.plane(r_tape,r_tile,0, r_tile,r_tape,-1, r_tile,r_tile,1)
        # alternative:
        # self.reflectance_mapping = plane(r_tape,r_tape,-1, r_tile,r_tape,0, r_tile,r_tile,1)

    ################################
    ### state functions    
    ################################
    ### All must be momentary and
    ### non-blocking, as the control
    ### loop takes place in 
    ### self.monitor_states
    ################################

    def start(self):
        if board.is_button_pressed():
            if 'on_state_switch' in self.verbosity: print("switching from start to random_walk")
            self.state = 'random_walk'

    def random_walk(self):
        # default behavior: 
        straight = random.uniform(0, 1) # a random float from 0 to 1
        turn = random.uniform(-1, 1)
        drivetrain.arcade(straight, turn)

        # state transfer behavior: 
        if rangefinder.distance() < 30:
            pass ## update state 

    ################################
    
    def follow_line(self):
        
        straight = 0.3
        turn = 0.02 * self.reflectance_mapping(reflectance.get_left(), reflectance.get_right())
        if 'reflectance_debug' in self.verbosity: 
            print('reflectance:', reflectance.get_left(), reflectance.get_right())
            print('arcade', straight, turn)
        drivetrain.arcade(straight, turn)

    def follow_wall(self):
        Kp = 0.03
        dist = self.median_distance() # in [cm]

        dist_error = self.target_wall_dist - dist

        if 'follow_wall_debug' in self.verbosity: print(self.target_wall_dist, dist, dist_error, Kp*dist_error)

        drivetrain.arcade(0.4, Kp*dist_error)

    ################################
    ### end state functions
    ################################

    ################################
    ### sensor-based functions
    ################################

    def median_distance(self):
        '''
        returns the median of the last n_to_mean rangefinder readings
        '''
        n_to_median = 5
        current_reading = rangefinder.distance()
        while current_reading == 65535: # @TODO do this more elegantly
            # this ignores any readings of 65535
            current_reading = rangefinder.distance()
        self.rangefinder_readings.append(current_reading)
        if len(self.rangefinder_readings) < n_to_median:
            return self.median_distance()
            # If we haven't taken many readings yet,
            # this recursive call should keep sampling
            # until we have a list of at least n_to_median
            # and then return the median of that.
        if len(self.rangefinder_readings) > n_to_median:
            self.rangefinder_readings.pop(0)
        return akmath.median(self.rangefinder_readings)

    def reflectance_error(self):
        '''
        synthesizes the value of 
        the left and right reflectance into
        a single float that represents
        the direction the robot should turn
        '''
        r_tile = 0.7704468
        r_tape = 0.7367401

        r_left = reflectance.get_left()
        r_right = reflectance.get_right()

        

        reflectance.get_left()
        reflectance.get_right()
        raise NotImplementedError

    ################################
    ### end sensor-based functions
    ################################

    def run(self):
        while not self.halt:
            time.sleep(0.5)

            print('self.state is: ')
            print(getattr(self, 'state'))

            getattr(self, self.state)()
            # this line executes the function whose name 
            # is the current value of the self.state string
    
    def test(self):
        while not self.halt:
            self.follow_wall()
            time.sleep(0.2)

active_fsm = LineWallFSM()

try:
    active_fsm.test()
except KeyboardInterrupt:
    drivetrain.stop()
    if 'general' in active_fsm.verbosity: print('stopped')
