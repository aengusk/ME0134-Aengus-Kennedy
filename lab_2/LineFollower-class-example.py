from XRPLib.defaults import *
from Husky.huskylensPythonLibrary import HuskyLensLibrary
import time

# Initialize HuskyLens on I2C and differential drive system
husky = HuskyLensLibrary("I2C")
differentialDrive = DifferentialDrive.get_default_differential_drive()

# Ensure HuskyLens is in line tracking mode
while not husky.line_tracking_mode():
    husky.line_tracking_mode()

base_velocity = 15
delta_velocity = 5

# Main loop
while True:
    state = husky.command_request_arrows()

    if len(state) > 0:
        state_vector = state[0]

        # x1 and x2 are the left and right points of the arrow
        state_x1 = state_vector[0]  # x1
        state_x2 = state_vector[2]  # x2

        # You could take either x1 or x2 as the X coordinate to track
        x = (state_x1 + state_x2) / 2  # center position of the line

        # Simple bang-bang controller
        if 140 <= x <= 180:
            # Go straight
            differentialDrive.set_speed(base_velocity, base_velocity)  # both motors at 60% speed

        elif x < 140:
            # Turn left
            differentialDrive.set_speed(base_velocity-delta_velocity, base_velocity+delta_velocity)  # left motor slower

        elif x > 180:
            # Turn right
            differentialDrive.set_speed(base_velocity+delta_velocity, base_velocity-delta_velocity)  # right motor slower

        print(f"X: {x}")

    else:
        # If no line detected, stop
        differentialDrive.set_speed(0.0, 0.0)

    time.sleep(0.1)