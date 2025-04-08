import time
import random
import akmath
from XRPLib.defaults import *
from Husky.huskylensPythonLibrary import HuskyLensLibrary as Husky

class LineWallFSM:
    def __init__(self):
        self.state = 'start'
        self.halt = False
        self.verbosity = ('general', 'on_state_switch', 'follow_line_debug', 'follow_wall_debug')
        # options: 'general', 'on_state_switch', 'follow_line_debug', 'follow_wall_debug'

        self.husky = Husky('I2C')
        self.husky.line_tracking_mode()

        self.rangefinder_readings = [] # to be median filtered

    states = [
        'start',
        'random_walk',
        'follow_line',
        'follow_wall'
    ]

    def choose_state(self):
        starting_state = self.state
        
        assert self.state in LineWallFSM.states, 'self.state not a valid state function'

        if self.state == 'start':
            if board.is_button_pressed():
                self.state = 'random_walk'

        elif self.state == 'random_walk':
            if self.there_is_a_wall():
                self.state = 'follow_wall'
            elif self.there_is_a_line():
                self.state = 'follow_line'

        elif self.state == 'follow_line':
            if not self.there_is_a_line():
                if self.there_is_a_wall():  
                    self.state = 'follow_wall'
                else:
                    self.state = 'random_walk'
        
        elif self.state == 'follow_wall':
            if not self.there_is_a_wall():
                if self.there_is_a_line():
                    self.state = 'follow_line'
                else:
                    self.state = 'random_walk'
        
        if 'on_state_switch' in self.verbosity:
            if starting_state != self.state:
                print('state switched from {} to {}'.format(starting_state, self.state))

    ################################
    ### state behavior functions
    ################################
    ### All must be momentary and
    ### non-blocking, as the control
    ### loop takes place in 
    ### self.choose_state
    ################################

    def start(self):
        pass

    def random_walk(self):
        straight = 0.6
        turn = random.uniform(-1, 1) # left (positive); right (negative)
        drivetrain.arcade(straight, turn)
        time.sleep(0.2)

    def follow_line(self):
        base_effort = 0.4 # 0.4 works; 0.35 works but is slow
        Kp = -0.002
        target_x = 160 # Target x-coordinate (center of camera view)

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

    def follow_wall(self):
        base_effort = 0.35
        Kp = 0.03
        target_wall_dist = 20 # [cm]

        dist = self.median_distance() # in [cm]

        dist_error = target_wall_dist - dist

        if 'follow_wall_debug' in self.verbosity:
            print(target_wall_dist, dist, dist_error, Kp*dist_error)

        drivetrain.set_effort(base_effort - Kp*dist_error, base_effort + Kp*dist_error)

    ################################
    ### end state behavior functions
    ################################

    ################################
    ### sensor-based functions
    ################################

    def median_distance(self):
        '''
        returns the median of the last n_to_median rangefinder readings
        '''
        n_to_median = 5
        current_reading = rangefinder.distance()
        while current_reading == 65535:
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
        returns True iff the HuskyLens sees a line to follow
        '''
        state = self.husky.command_request_arrows() # type: List[List[int]] # type: ignore
        return len(state) > 0

    def there_is_a_wall(self):
        '''
        returns True iff the rangefinder
        indicatesd that it sees a wall to follow
        '''
        return self.median_distance() < 40

    ################################
    ### end sensor-based functions
    ################################

    def run(self):
        while not self.halt:
            if 'general' in self.verbosity:
                print('self.state is: ')
                print(getattr(self, 'state'))

            self.choose_state() # Choose next state based on conditions
            
            getattr(self, self.state)() # Execute current state's behavior
            # this line executes the function whose name 
            # is the current value of the self.state string
    
    def test(self):
        while not self.halt:
            self.follow_wall()
            #print('there is a line: {}\nthere is a wall: {}\n'.format(self.there_is_a_line(), self.there_is_a_wall()))
            time.sleep(0.05)

active_fsm = LineWallFSM()

try:
    active_fsm.run()
except KeyboardInterrupt:
    drivetrain.stop()
    if 'general' in active_fsm.verbosity: print('stopped')
