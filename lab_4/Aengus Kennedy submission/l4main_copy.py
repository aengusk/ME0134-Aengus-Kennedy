import time
from XRPLib.imu import IMU
from XRPLib.differential_drive import DifferentialDrive
import akmath

drivetrain = DifferentialDrive.get_default_differential_drive()
imu = IMU.get_default_imu() 
# imu.running_yaw is in degrees counterclockwise

data = []
data_start_time = time.ticks_ms()

def log():
    data.append((time.ticks_ms() - data_start_time, drivetrain.get_left_encoder_position(), drivetrain.get_right_encoder_position(), imu.running_yaw))

def save_data():
    with open('l4data.csv', 'w') as f:
        for row in data:
            f.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

def drive_forward(dist, speed = 100): # where dist is in [cm] and speed is in [cm / second]
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - start_time < abs(dist/speed) * 1000:
        log()
        time.sleep(0.1)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

def turn(dist, speed = 100): # where dist is in [cm of arc] and speed is in [cm / second]
    # wheelbase diameter is 15.24 cm
    # 180 degrees is 23.9389360204 cm of arc
    # 1 rotation  is 47.8778720407
    # 2 rotations is 95.7557440814
    # 8 rotations is 383.022976326
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed, -speed)
    while time.ticks_ms() - start_time < abs(dist/speed) * 1000:
        log()
        time.sleep(0.1)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

def experiment():

    # Drive forward 2 meters at high speed
    drive_forward(200, 150)
    time.sleep(0.5)
    
    # Turn 1.5 rotations at high speed
    turn(47.8778720407 * 1.5, 150)
    time.sleep(0.5)

    # Drive forward 5 meters at high speed
    drive_forward(500, 150)
    time.sleep(0.5)
    
    # Do 2.5 rotations at high speed
    turn(47.8778720407 * 2.5, 150)
    time.sleep(0.5)
    
    # Final high speed straight run
    drive_forward(150, 150)

    # Do 8 full rotations at high speed
    turn(47.8778720407 * 11, 100) # 8 rotations of a 15.24 cm wheelbase is 383.022976326 cm of arc

    # Drive forward 4 meters at medium speed
    drive_forward(400, 50)
    time.sleep(0.5)

    save_data()

def main():
    experiment()

if __name__ == '__main__':
    main()
