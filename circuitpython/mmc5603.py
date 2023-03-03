""" 
mmc5983.py

    circuitpython driver lib for mmc5983 magnetometer
    currently is just a set-it-and-forget-it dealio for the FP/mainboard usage

C. Hillis 3/22
"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bits import ROBits, RWBits
from adafruit_register.i2c_bit import ROBit, RWBit
from adafruit_register.i2c_struct import UnaryStruct

# Register Map
XOUT0               = const(0x00) #Xout [17:10]
XOUT1               = const(0x01) #Xout [9:2]
YOUT0               = const(0x02)
YOUT1               = const(0x03)
ZOUT0               = const(0x04)
ZOUT1               = const(0x05)
XYZOUT              = const(0x06) #Xout[1:0], Yout[1:0], Zout[1:0]
TOUT                = const(0x07)
STATUS              = const(0x08)
INTERNAL_CONTROL_0  = const(0x09)
INTERNAL_CONTROL_1  = const(0x0A)
INTERNAL_CONTROL_2  = const(0x0B)
INTERNAL_CONTROL_3  = const(0x0C)
PRODUCT_ID_1        = const(0x2F)

class MMC5983:

    # Class Variables (NOT ALL REGISTERS AND FUNCTIONS ARE IMPLEMENTED)
    _xout0 = UnaryStruct(XOUT0, "<B")
    _xout1 = UnaryStruct(XOUT1, "<B")
    _yout0 = UnaryStruct(YOUT0, "<B")
    _yout1 = UnaryStruct(YOUT1, "<B")
    _zout0 = UnaryStruct(ZOUT0, "<B")
    _zout1 = UnaryStruct(ZOUT1, "<B")
    _xyzout = UnaryStruct(XYZOUT, "<B")
    _tout = UnaryStruct(TOUT, "<B")
    _meas_m_done = RWBit(STATUS, 0)
    _meas_t_done = RWBit(STATUS, 1)
    _otp_rd_done = RWBit(STATUS, 4)
    _tm_m = RWBit(INTERNAL_CONTROL_0, 0)
    _tm_t = RWBit(INTERNAL_CONTROL_0, 1)
    _int_meas_done_en = RWBit(INTERNAL_CONTROL_0, 2)
    _auto_sr_en = RWBit(INTERNAL_CONTROL_0, 5)
    _bw = RWBits(2, INTERNAL_CONTROL_1, 0)
    _inhibit = RWBits(3, INTERNAL_CONTROL_1, 2)
    _reset = RWBit(INTERNAL_CONTROL_1, 7)
    _cm_freq = RWBits(3, INTERNAL_CONTROL_2, 0)
    _cmm_en = RWBit(INTERNAL_CONTROL_2, 3)
    _prd_set = RWBits(3, INTERNAL_CONTROL_2, 4)
    _en_prd_set = RWBit(INTERNAL_CONTROL_2, 7)
    _st_en_p = RWBit(INTERNAL_CONTROL_3, 1)
    _st_en_n = RWBit(INTERNAL_CONTROL_3, 2)
    _p_id = ROBits(4, PRODUCT_ID_1, 4)

    class _BAD_P_ID(Exception):
        pass

    def __init__(self, i2c_bus, addr):
        self.i2c_device = I2CDevice(i2c_bus, addr, probe=False)
        test = self._p_id
        if not test == 3 : raise self._BAD_P_ID("[ERROR][MMC5983][BAD P_ID VALUE]: "+ str(test))
        self.ON()

    def ON(self):
        #self.reset()
        if(self._otp_rd_done==True):
            self._inhibit = 0 #disables inhibits
            self._bw = 0 #100Hz BW,  measurement time 8ms
            self._cmfreq = 5 #100Hz continuous measurements -- w/ 8ms measurement time
            self._cmm_en = True
            self.prd_set = 6 #every 1000 measurements the device will set/reset the coils (~10sec)
            self._en_prd_set = True
            self._int_meas_done_en = True
        
    def SLEEP(self):
        #self.reset()
        self.inhibit = 7 #inhibits the magnetometers
        self.cmm_en = False #auto measurements off
        self.en_prd_set = False # auto set/reset is off just in case 

    #function calling this needs to be aware of this taking 10ms
    def reset(self):
        self._reset = True

    @property
    def read(self):
        out = self.read_raw
        for meas in range(len(out)):
            out[meas] = ((out[meas]-131072)/16384/0.01)# adjusts raw values to uT, sensor default sensitivity is 16384 counts/G, unsigned, null offset is 131072, 1uT/0.01G
        return(out)

    @property
    def read_raw(self):
        self._tm_m = 1 # should NOT have to set this why doesn't the auto-measurements work?
        x = (self._xout0 << 10) + (self._xout1 << 2) + (self._xyzout >> 6)
        y = (self._yout0 << 10) + (self._yout1 << 2) + ((self._xyzout & 0x30) >> 4)
        z = (self._zout0 << 10) + (self._zout1 << 2) + ((self._xyzout & 0xC) >> 2)
        out = [x, y, z]
        self.meas_t_done = True # writing 1 resets this interrupt
        return(out)
        
    @property
    def temp(self): #datasheet says 0.8degC per cnt, -75degC offset
        self._tm_t = True
        temp = (self._tout * 0.8) - 75
        return(temp)

    # @property
    # def auto_sr(self):
    #     return(self._auto_sr_en) # 1 for on 0 for off, not really sure what the benefits of this are.
    # @auto_sr.setter
    # def auto_sr(self, value):
    #     self._auto_sr_en = value
    
    # @property
    # def bw(self):
    #     return(self._bw)
    # @bw.setter
    # def bw(self, value):
    #     self._bw = value

    # @property
    # def cm_freq(self):
    #     return(self._cm_freq)
    # @cm_freq.setter
    # def cm_freq(self, value):
    #     self._cm_freq = value

    # @property
    # def cmm_en(self):
    #     return(self._cmm_en)
    # @cmm_en.setter
    # def cmm_en(self, value):
    #     self._cmm_en = value

    # @property
    # def prd_set(self):
    #     return(self._prd_set)
    # @prd_set.setter
    # def prd_set(self, value):
    #     self._prd_set = value

    # @property
    # def en_prd_set(self):
    #     return(self._en_prd_set)
    # @en_prd_set.setter
    # def en_prd_set(self, value):
    #     self._en_prd_set = value

    # @property
    # def otp_rd_done(self):
    #     return(self._otp_rd_done)
    # @otp_rd_done.setter
    # def otp_rd_done(self, value):
    #     self._otp_rd_done = value
    
    # @property
    # def meas_m_done(self):
    #     return(self._meas_m_done)
    # @meas_m_done.setter
    # def meas_m_done(self, value):
    #     self._otp_rd_done = value

    #def selftest(self): #self tests magnetic sensors for saturation, not impllemented