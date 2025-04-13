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

print('about to start logging')

for i in range(100):
    log()
    time.sleep(0.1)

save_data()
print('saved data')
