# from XRPLib.deafaults import *
from XRPLib.differential_drive import DifferentialDrive
from XRPLib.encoded_motor import EncodedMotor

drivetrain = DifferentialDrive.get_default_differential_drive()
# right_motor = EncodedMotor.get_default_encoded_motor(index=2)

drivetrain.set_speed(1.0, 1.0)

drivetrain.left_motor.speedController.clear_history(); drivetrain.right_motor.speedController.clear_history()