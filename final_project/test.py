import time
from XRPLib.board import Board
from XRPLib.differential_drive import DifferentialDrive

board = Board.get_default_board()

drivetrain = DifferentialDrive.get_default_differential_drive()

driving = False

print('ready to drive...')

while True:
    if not driving:
        if board.is_button_pressed():
            driving = True
            drivetrain.set_speed(10.0, 10.0)
            print('set speed 10, 10')
            time.sleep(0.5)
    else: # driving
        if board.is_button_pressed():
            driving = False
            drivetrain.set_speed(0.0, 0.0)
            print('set speed 0, 0')
            drivetrain.left_motor.speedController.clear_history(); drivetrain.right_motor.speedController.clear_history()
            time.sleep(0.5)