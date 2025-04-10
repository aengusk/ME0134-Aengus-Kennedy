import time
from XRPLib.differential_drive import DifferentialDrive

drivetrain = DifferentialDrive.get_default_differential_drive()

data = []
data_start_time = time.ticks_ms()

def log():
    data.append((time.ticks_ms() - data_start_time, drivetrain.get_left_encoder_position(), drivetrain.get_right_encoder_position()))

def forward_and_return():
    speed = 10 # cm/s
    print('Driving forward for 10 seconds...')
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - start_time < 10000:
        log()
        time.sleep(0.05)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

    time.sleep(1)

    print('Turning 180 degrees...')
    log()
    drivetrain.turn(180, 1, use_imu=False)
    log()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

    time.sleep(1)

    print('Driving forward for 10 seconds...')
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - start_time < 10000:
        log()
        time.sleep(0.05)
    drivetrain.stop()

def forward_and_turn():
    speed = 10 # cm/s
    print('Driving forward for 5 seconds...')
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - start_time < 5000:
        log()
        time.sleep(0.05)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

    time.sleep(1)

    print('Driving in a curve for 5 seconds...')
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed/2, speed)
    while time.ticks_ms() - start_time < 5000:
        log()
        time.sleep(0.05)
    drivetrain.stop()
    log()

def circle():
    speed = 10 / 1.375 # cm/s, determined to be about 30 sec/revolution
    print('Driving in a circle for 30 seconds...')
    start_time = time.ticks_ms()
    drivetrain.set_speed(speed/2 , speed)
    while time.ticks_ms() - start_time < 30000:
        log()
        time.sleep(0.2)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

def circle2():
    l_r_ratio = 0.004985 / 0.036903
    l_speed = 0.5 / 0.875 / (340/360) # cm/s, determined to be about 30 sec/revolution
    r_speed = l_speed / l_r_ratio

    print('Driving in a circle for 30 seconds...')
    start_time = time.ticks_ms()
    drivetrain.set_speed(l_speed, r_speed)
    while time.ticks_ms() - start_time < 30000:
        log()
        time.sleep(0.2)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()

def save_data():
    with open('data.csv', 'w') as f:
        for row in data:
            f.write(f"{row[0]},{row[1]},{row[2]}\n")

if __name__ == "__main__":
    circle()
    save_data()
