"""
imu-stamp.py

CircuitPython lib for imu-stamp rev.A

Caden H. 3/3/23
"""

import iam20380
import mc3419
import mmc5603
from micropython import const

#DATA_BUFFER_SIZE = const(2)

# Calibrated Acceleration (m/s2)
REPORT_ACCELEROMETER = const(0x01)
# Calibrated gyroscope (rad/s).
REPORT_GYROSCOPE = const(0x02)
# Magnetic field calibrated (in µTesla). 
REPORT_MAGNETOMETER = const(0x03)
# Linear acceleration (m/s2). Acceleration of the device.

REPORT_RAW_ACCELEROMETER = const(0x14)
REPORT_RAW_GYROSCOPE = const(0x15)
REPORT_RAW_MAGNETOMETER = const(0x16)

class IMUstamp:

    def __init__(self, xor1, xor2, debug = False, reset = False): #insert optional variables for ignoring devices?
        """
        Init routine
        """
        self._debug = debug
        self._reset = reset
        self._dbg("********** __init__ imu-stamp *************")
        '''
        self._data_buffer = bytearray(DATA_BUFFER_SIZE)
        self._command_buffer = bytearray(12)
        '''
        self._wait_for_initialize = True
        self._init_complete = False
        self._id_read = False
        self._readings = {}
        self.initialize()

        self.gyro0 = iam20380.IAM20380()
        self.gyro1 = iam20380.IAM20380()
        self.accel0 = mc3419.MC3419()
        self.accel1 = mc3419.MC3419()
        self.mag0 = mmc5603.MMCC5603()
        self.mag1 = mmc5603.MMCC5603()

    def initialize():
        """Initialize the sensor"""
        for _ in range(3):
            self.hard_reset()
            self.soft_reset()
            try:
                if self._check_id():
                    break
            except:  # pylint:disable=bare-except
                time.sleep(0.5)
        else:
            raise RuntimeError("Could not read ID")

    @property
    def magnetic(self):
        """A tuple of the current magnetic field measurements on the X, Y, and Z axes"""
        self._process_available_packets()  # decorator?
        try:
            return self._readings[BNO_REPORT_MAGNETOMETER]
        except KeyError:
            raise RuntimeError("No magfield report found, is it enabled?") from None
        
    @property
    def acceleration(self):
        """A tuple representing the acceleration measurements on the X, Y, and Z
        axes in meters per second squared"""
        self._process_available_packets()
        try:
            return self._readings[BNO_REPORT_ACCELEROMETER]
        except KeyError:
            raise RuntimeError("No accel report found, is it enabled?") from None
        
    @property
    def gyro(self):
        """A tuple representing Gyro's rotation measurements on the X, Y, and Z
        axes in radians per second"""
        self._process_available_packets()
        try:
            return self._readings[BNO_REPORT_GYROSCOPE]
        except KeyError:
            raise RuntimeError("No gyro report found, is it enabled?") from None
        
    @property
    def raw_acceleration(self):
        """Returns the sensor's raw, unscaled value from the accelerometer registers"""
        self._process_available_packets()
        try:
            raw_acceleration = self._readings[BNO_REPORT_RAW_ACCELEROMETER]
            return raw_acceleration
        except KeyError:
            raise RuntimeError(
                "No raw acceleration report found, is it enabled?"
            ) from None

    @property
    def raw_gyro(self):
        """Returns the sensor's raw, unscaled value from the gyro registers"""
        self._process_available_packets()
        try:
            raw_gyro = self._readings[BNO_REPORT_RAW_GYROSCOPE]
            return raw_gyro
        except KeyError:
            raise RuntimeError("No raw gyro report found, is it enabled?") from None

    @property
    def raw_magnetic(self):
        """Returns the sensor's raw, unscaled value from the magnetometer registers"""
        self._process_available_packets()
        try:
            raw_magnetic = self._readings[BNO_REPORT_RAW_MAGNETOMETER]
            return raw_magnetic
        except KeyError:
            raise RuntimeError("No raw magnetic report found, is it enabled?") from None
        
    def hard_reset(self):
        """Hardware reset the sensor to an initial unconfigured state"""
        if not self._reset:
            return
        import digitalio  # pylint:disable=import-outside-toplevel

        self._reset.direction = digitalio.Direction.OUTPUT
        self._reset.value = True
        time.sleep(0.01)
        self._reset.value = False
        time.sleep(0.01)
        self._reset.value = True
        time.sleep(0.01)

    def soft_reset(self):
        """Reset the sensor to an initial unconfigured state"""
        self._dbg("Soft resetting...", end="")
        data = bytearray(1)
        data[0] = 1
        _seq = self._send_packet(BNO_CHANNEL_EXE, data)
        time.sleep(0.5)
        _seq = self._send_packet(BNO_CHANNEL_EXE, data)
        time.sleep(0.5)

        for _i in range(3):
            try:
                _packet = self._read_packet()
            except PacketError:
                time.sleep(0.5)

        self._dbg("OK!")
        # all is good!