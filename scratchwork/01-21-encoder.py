from XRPLib.encoder import Encoder
from XRPLib.encoder import Encoder

from time import sleep

x = Encoder(0, 4, 5)

while True:
    print('left encoder reading [rotations]: {}'.format(x.get_position()))
    sleep(1)