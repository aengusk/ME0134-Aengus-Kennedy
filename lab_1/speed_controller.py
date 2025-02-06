from XRPLib.board import Board
from XRPLib.encoder import Encoder
from XRPLib.motor import Motor
import time
import math

board = Board.get_default_board()

# Define pins
LEFT_ENCODER_A = 4  
LEFT_ENCODER_B = 5  
RIGHT_ENCODER_A = 12
RIGHT_ENCODER_B = 13

LEFT_MOTOR_A = 6
LEFT_MOTOR_B = 7
RIGHT_MOTOR_A = 14
RIGHT_MOTOR_B = 15

# Instantiate Encoder class
left_motor_encoder = Encoder(index=0, encAPin=LEFT_ENCODER_A, encBPin=LEFT_ENCODER_B)
right_motor_encoder = Encoder(index=1, encAPin=RIGHT_ENCODER_A, encBPin=RIGHT_ENCODER_B)

# Instantiate Motor class
left_motor = Motor(LEFT_MOTOR_A, LEFT_MOTOR_B,flip_dir=True) # NOTE negative sign
right_motor = Motor(RIGHT_MOTOR_A, RIGHT_MOTOR_B)
left_motor.set_effort(0)
right_motor.set_effort(0)

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.error_sum = 0
        self.error_delta = 0
        self.prev_error = 0
        self.last_time = time.ticks_ms()
        self.curr_time = self.last_time
        
    def update(self, error):
        #### DONE: implement the PID controller here ####
        self.curr_time = time.ticks_ms()
        Δt = (self.curr_time - self.last_time) / 1000 # in [seconds]

        self.error_sum +=  error * Δt
        self.error_delta = (error - self.prev_error) / Δt

        effort = self.Kp * error + self.Ki * self.error_sum + self.Kd * self.error_delta

        self.last_time = time.ticks_ms()
        self.prev_error = error
        return effort

# Parameters for speed control
counts_per_wheel_revolution = (30/14) * (28/16) * (36/9) * (26/8) * 12 # 585
wheel_diameter = 60 #mm
circumference_wheel = math.pi*wheel_diameter #188.49mm

speed_left_target = 100 #### PARAM choose your speed target [mm/s]
speed_right_target = speed_left_target

test_duration = 10 # s
sampling_time = 0.05 #### PARAM: choose your sampling time [s]

# controller constants
Kp_left = 0.003     #### PARAM: find your Kp
Ki_left = 0.02      #### PARAM: find your Ki
Kd_left = 0         #### PARAM: find your Kd
Kp_right = Kp_left
Ki_right = Ki_left
Kd_right = Kd_left
    
speed_left_controller = PIDController(Kp_left, Ki_left, Kd_left)
speed_right_controller = PIDController(Kp_right, Ki_right, Kd_right)

print_debugs = False
data_speed_only = False
data_speed_effort_error = True

data = []

def calculate_speed():
    #### DONE: calculate speed with encoder count ####

    Δt = (current_time - last_time) / 1000 # in [seconds]

    left_Δcounts = curr_counts_left - last_counts_left
    right_Δcounts = curr_counts_right - last_counts_right

    if print_debugs:
        print('curr_counts: ', curr_counts_left, curr_counts_right)

    if print_debugs:
        print('Δcounts: ', left_Δcounts, right_Δcounts)

    left_cps = left_Δcounts / Δt # in [counts / second]
    right_cps = right_Δcounts / Δt # in [counts / second]

    speed_left = left_cps   / counts_per_wheel_revolution * circumference_wheel # [in mm/s]
    speed_right = right_cps / counts_per_wheel_revolution * circumference_wheel # [in mm/s]

    if print_debugs:
        print('speeds:  ', speed_left, speed_right)

    return speed_left, speed_right

def set_effort_manually(effort):
    left_motor.set_effort(effort)
    right_motor.set_effort(effort)


def update_effort(speed_left, speed_right):
    #### DONE: update motor effort according to the current speed ####

    # speed_left, speed_right = calculate_speed()

    error_left = speed_left_target - speed_left
    error_right = speed_right_target - speed_right

    if print_debugs:
        print('error:  ', error_left, error_right)

    left_effort = speed_left_controller.update(error_left)
    right_effort = speed_right_controller.update(error_right)
    
    if print_debugs:
        print('effort:   ', left_effort, right_effort)

    left_motor.set_effort(left_effort) # NOTE negative sign
    right_motor.set_effort(right_effort)

    # These only need to be returned when collecting data to plot. 
    return error_left, error_right, left_effort, right_effort

print("Waiting for start button...")
# board.wait_for_button()  # Wait for the button to start # NOTE TODO temporarily disabled wait for button
print("Started! Press the button again to stop.")

last_counts_left = -left_motor_encoder.get_position_counts() # NOTE negative sign
curr_counts_left = -left_motor_encoder.get_position_counts() # NOTE negative sign

last_counts_right = right_motor_encoder.get_position_counts()
curr_counts_right = right_motor_encoder.get_position_counts()

init_time = time.ticks_ms()
last_time = init_time
current_time = init_time
while (current_time - init_time)/1000 <= test_duration:
    if board.is_button_pressed():  # Check if the button is pressed to stop
        print("Stopped!")
        left_motor.set_effort(0)
        right_motor.set_effort(0)
        board.wait_for_button()  # Wait for button release to avoid immediate restart
        break
    
    current_time = time.ticks_ms()
    curr_counts_left = -left_motor_encoder.get_position_counts() # NOTE negative sign
    curr_counts_right = right_motor_encoder.get_position_counts()

    wait_time = (current_time - last_time)/1000 # convert from ms to s
    if wait_time > sampling_time:
        speed_left, speed_right = calculate_speed()
        
        # set_effort_manually(1) # use this for the beginning of the lab
        
        if data_speed_only:
            data.append((speed_left, speed_right))
        
        # These returns are only used to collect data to graph
        error_left, error_right, left_effort, right_effort = update_effort(speed_left, speed_right)
        
        if data_speed_effort_error:
            data.append(
                (
                    (speed_left, left_effort, error_left),
                    (speed_right, right_effort, error_right)
                )
            )

        last_time = current_time
        last_counts_left = curr_counts_left
        last_counts_right = curr_counts_right
        # print(current_time - init_time, speed_left, speed_right)

left_motor.set_effort(0)
right_motor.set_effort(0)
print(data)