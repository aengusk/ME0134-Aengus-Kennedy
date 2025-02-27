from time import sleep
from XRPLib.defaults import reflectance

def collect_data():
    while True:
        print(reflectance.get_right())
        sleep(1)

collect_data()