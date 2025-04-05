import time
import random
import akmath
from XRPLib.defaults import *
from Husky.huskylensPythonLibrary import HuskyLensLibrary as Husky

class LineWallFSM:
    def __init__(self):
        # program flow
        self.state = 'start'
        self.halt = False
        self.verbosity = ('general', 'on_state_switch', 'follow_line_debug', 'follow_wall_debug')
        # options: 'general', 'on_state_switch', 'follow_line_debug', 'follow_wall_debug'

        # # line following & reflectance sensor
        # self.r_tile = 0.7704468
        # self.r_tape = 0.7367401

        # Initialize HuskyLens
        self.husky = Husky('I2C')
        # Put HuskyLens is in line tracking mode
        self.husky.line_tracking_mode()

        # wall following & rangefinder
        self.rangefinder_readings = []
        self.target_wall_dist = 15 # [cm]

    ################################
    ### behavior functions
    ################################

    states = [
        'start',
        'random_walk',
        'follow_line_find_wall',
        'follow_wall_ignore_line',
        'follow_wall_find_line',
        'follow_line_ignore_wall'
    ]

    def choose_state(self):
        starting_state = self.state
        
        assert self.state in LineWallFSM.states, 'self.state not found, it may have been typed incorrectly' # @TODO remove

        if self.state == 'start':
            if board.is_button_pressed():
                self.state = 'random_walk'

        elif self.state == 'random_walk':
            if self.there_is_a_line():
                self.state = 'follow_line_find_wall'
            elif self.there_is_a_wall():
                self.state = 'follow_wall_find_line'

        elif self.state == 'follow_line_find_wall':
            if self.there_is_a_wall():
                self.state = 'follow_wall_ignore_line'
            elif not self.there_is_a_line():
                self.state = 'random_walk'
        
        elif self.state == 'follow_wall_ignore_line':
            raise NotImplementedError
            if not self.there_is_a_line():
                self.state = 'follow_wall_find_line'
            elif not self.there_is_a_wall():
                raise NotImplementedError
        
        elif self.state == 'follow_wall_find_line':
            if self.there_is_a_line():
                self.state = 'follow_line_ignore_wall'
            elif not self.there_is_a_wall():
                self.state = 'random_walk'
        
        elif self.state == 'follow_line_ignore_wall':
            raise NotImplementedError
        
        if 'on_state_switch' in self.verbosity:
            if starting_state != self.state:
                print('state switched from {} to {}'.format(starting_state, self.state))

    ################################
    ### end behavior functions
    ################################

    ################################
    ### behavior functions
    ################################
    ### All must be momentary and
    ### non-blocking, as the control
    ### loop takes place in 
    ### self.monitor_states
    ################################

    def random_walk(self):
        # default behavior: 
        straight = random.uniform(0, 1) # a random float from 0 to 1
        turn = random.uniform(-1, 1)
        drivetrain.arcade(straight, turn)

        # state transfer behavior: 
        if rangefinder.distance() < 30:
            pass ## update state 

    ################################

    def follow_wall(self):
        Kp = 0.03
        dist = self.median_distance() # in [cm]

        dist_error = self.target_wall_dist - dist

        if 'follow_wall_debug' in self.verbosity: print(self.target_wall_dist, dist, dist_error, Kp*dist_error)

        drivetrain.arcade(0.4, Kp*dist_error)

    def follow_line(self):
        # Line following parameters
        base_effort = 0.375
        Kp = -0.01  # Proportional gain for HuskyLens line following
        target_x = 160  # Target x-coordinate (center of camera view)

        # Get line position from HuskyLens
        state = self.husky.command_request_arrows() # type: List[List[int]] # type: ignore
        # Calculate error from line position
        if len(state) > 0:
            state_vector = state[0]
            # x1 and x2 are the left and right points of the line
            state_x1 = state_vector[0]  # x1
            state_x2 = state_vector[2]  # x2
            
            # Calculate center position of the line
            x = (state_x1 + state_x2) / 2
            
            # Calculate error (difference from target position)
            error = x - target_x
            
            if 'follow_line_debug' in self.verbosity:
                print(f"Line position: {x}, Error: {error}")
        else:
            error = 0
        # Apply proportional control and drive
        # Negative Kp because we want to turn in opposite direction of error
        turn = Kp * error
        
        # Set motor efforts using arcade drive
        # base_effort for forward motion, turn for steering
        drivetrain.arcade(base_effort, turn)
        if len(state) > 0:
            state_vector = state[0]
            # x1 and x2 are the left and right points of the line
            state_x1 = state_vector[0]  # x1
            state_x2 = state_vector[2]  # x2
            
            # Calculate center position of the line
            x = (state_x1 + state_x2) / 2
            
            # Calculate error (difference from target position)
            error = x - target_x
            
            if 'follow_line_debug' in self.verbosity:
                print(f"Line position: {x}, Error: {error}")
            
            # Apply proportional control
            # Negative Kp because we want to turn in opposite direction of error
            turn = Kp * error
            
            # Set motor efforts using arcade drive
            # base_effort for forward motion, turn for steering
            drivetrain.arcade(base_effort, turn)
        else:
            # If no line detected, stop
            drivetrain.stop()

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
    
    def there_is_a_line(self):
        '''
        returns True iff either reflectance sensor
        indicates that it sees a line to follow
        '''
        state = self.husky.command_request_arrows() # type: List[List[int]] # type: ignore
        return len(state) > 0

    def there_is_a_wall(self):
        '''
        returns True iff the rangefinder
        indicatesd that it sees a wall to follow
        ''' # @TODO filter for reliability
        return rangefinder.distance() < 60

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
            self.follow_line()
            #print('there is a line: {}\nthere is a wall: {}\n'.format(self.there_is_a_line(), self.there_is_a_wall()))
            time.sleep(0.05)

active_fsm = LineWallFSM()

try:
    active_fsm.test()
except KeyboardInterrupt:
    drivetrain.stop()
    if 'general' in active_fsm.verbosity: print('stopped')
