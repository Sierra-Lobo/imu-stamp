"""
imu-stamp.py

CircuitPython lib for imu-stamp rev.A

Caden H. 3/3/23
"""

from sierralobo_iam20380 import IAM20380
from sierralobo_mc3419 import MC3419
from adafruit_mmc5603 import MMC5603
from micropython import const

_IAM20380_ADDR = const(0x68)
_MC3419_ADDR = const(0x4C)
_MMC5603_ADDR = const(0x30)

class imu:

    def __init__(self, i2c_bus, xor1, xor2):
        """Initalize IMU ICs"""

        self.gyro0 = IAM20380(i2c_bus, address = _IAM20380_ADDR ^ xor1)
        self.gyro1 = IAM20380(i2c_bus, address = _IAM20380_ADDR ^ xor2)
        self.accel0 = MC3419(i2c_bus, address = _MC3419_ADDR ^ xor1)
        self.accel1 = MC3419(i2c_bus, address = _MC3419_ADDR ^ xor2)
        self.mag0 = MMC5603(i2c_bus, address = _MMC5603_ADDR ^ xor1)
        self.mag1 = MMC5603(i2c_bus, address = _MMC5603_ADDR ^ xor2)

    def soft_reset(self):
        self.gyro0.reset()
        self.gyro1.reset()
        self.accel0.reset()
        self.accel1.reset()
        self.mag0.reset()
        self.mag1.reset()