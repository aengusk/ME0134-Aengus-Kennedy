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

def drive_forward(dist, speed = 100): # where dist is in cm and speed is in cm per second
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed, speed) # 100 cm per second
    while time.ticks_ms() - start_time < dist/speed * 1000:
        log()
        time.sleep(0.1)
    drivetrain.stop()

def turn(angle, speed = 100): # where angle is in degrees and speed is in cm per second
    raise NotImplementedError

def main():
    drive_forward(20, 50)

if __name__ == '__main__':
    main()
