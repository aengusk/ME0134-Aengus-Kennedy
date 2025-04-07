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

        # Line position median filter
        self.line_x_readings = []

        # wall following & rangefinder
        self.rangefinder_readings = []


    ################################
    ### behavior functions
    ################################

    states = [
        'start',
        'random_walk',
        'follow_line',
        'follow_wall'
    ]

    def choose_state(self):
        starting_state = self.state
        
        assert self.state in LineWallFSM.states, 'self.state not found, it may have been typed incorrectly' # @TODO remove

        if self.state == 'start':
            self.state = 'random_walk'
            # if board.is_button_pressed():
            #     self.state = 'random_walk'

        elif self.state == 'random_walk':
            if self.there_is_a_line():
                self.state = 'follow_line'
            elif self.there_is_a_wall():
                self.state = 'follow_wall'

        elif self.state == 'follow_line':
            if not self.there_is_a_line():
                if self.there_is_a_wall():
                    self.state = 'follow_wall'
                else:
                    self.state = 'random_walk'
        
        elif self.state == 'follow_wall':
            if self.there_is_a_line():
                self.state = 'follow_line'
            elif not self.there_is_a_wall():
                self.state = 'random_walk'
        
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
        straight = 0.5
        turn = random.uniform(-0.5, 0.5)
        drivetrain.arcade(straight, turn)

    def start(self):
        pass

    def follow_wall(self):
        base_effort = 0.35
        Kp = 0.03
        target_wall_dist = 15 # [cm]
        dist = self.median_distance() # in [cm]

        dist_error = target_wall_dist - dist

        if 'follow_wall_debug' in self.verbosity:
            print(target_wall_dist, dist, dist_error, Kp*dist_error)

        drivetrain.set_effort(base_effort - Kp*dist_error, base_effort + Kp*dist_error)

    def follow_line(self):
        # Line following parameters
        base_effort = 0.35
        Kp = -0.002  # Proportional gain for HuskyLens line following
        target_x = 160  # Target x-coordinate (center of camera view)

        # # Get filtered line position
        # x = self.median_line_position()
        
        state = self.husky.command_request_arrows() # type: List[List[int]] # type: ignore
        if len(state) > 0:
            x2 = state[0][2]
            error = x2 - target_x
            
            if 'follow_line_debug' in self.verbosity:
                print(f"Arrow tip x2: {x2}, Error: {error}")
            
        else:
            # If no line detected, drive straight
            error = 0
            if 'follow_line_debug' in self.verbosity:
                print(f"No line detected, driving straight")
        turn = Kp * error
        # error is positive means turn right; error is negative means turn left
        drivetrain.set_effort(base_effort - turn, base_effort + turn)

    ################################
    ### end state functions
    ################################

    ################################
    ### sensor-based functions
    ################################

    def median_line_position(self):
        '''
        returns the median of the last n_to_median line position readings
        '''
        n_to_median = 5
        state = self.husky.command_request_arrows() # type: List[List[int]] # type: ignore
        if len(state) > 0:
            state_vector = state[0]
            x0, x1 = state_vector[0], state_vector[2]
            if 'follow_line_debug' in self.verbosity:
                print(f'x0: {x0}, x1: {x1}')
            current_reading = (x0 + x1)/2
            self.line_x_readings.append(current_reading)
            if len(self.line_x_readings) < n_to_median:
                return self.median_line_position()
            if len(self.line_x_readings) > n_to_median:
                self.line_x_readings.pop(0)
            return akmath.median(self.line_x_readings)
        return None

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

            # Choose next state based on conditions
            self.choose_state()
            
            # Execute current state's behavior
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
    active_fsm.run()
except KeyboardInterrupt:
    drivetrain.stop()
    if 'general' in active_fsm.verbosity: print('stopped')
