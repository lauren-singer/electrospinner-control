from __future__ import print_function

import serial
import time

class NewEraPump(serial.Serial):
    """
    This class is designed to control a New Era Syringe Pump.
    www.syringepump.com
    """
    
    status = None
    rateUnit = None
    direction = None
    diameter = None
    
    ETX = '\x03'    # End of packet transmission
    STX = '\x02'    # Start of packet transmission
    CR  = '\x0D'    # Carriage return
    
    STATUS = dict(I='infusing', W='withdrawing', S='halted', P='paused',
              T='in timed pause', U='waiting for trigger', X='purging',
              A='alarm')
              
    DIR_MODE = {
            'INF':  'infuse',
            'WDR':  'withdraw',
            'REV':  'reverse',
            }

    REV_DIR_MODE = dict((v, k) for k, v in DIR_MODE.items())

    RATE_UNIT = {
            'UM':   'ul/min',
            'MM':   'ml/min',
            'UH':   'ul/h',
            'MH':   'ml/h',
            }

    REV_RATE_UNIT = dict((v, k) for k, v in RATE_UNIT.items())

    VOL_UNIT = {
            'UL':   'ul',
            'ML':   'ml',
            }
    
    def __init__(self,port,timeout=0.5,debug=False):
        params = {
                'timeout'  : timeout,
                'baudrate' : 19200,
                'bytesize' : serial.EIGHTBITS,
                'parity'   : serial.PARITY_NONE,
                'stopbits' : serial.STOPBITS_ONE,
                }
        super(NEPump,self).__init__(port,**params)
        self.debug=debug
        self._sendCmd("ADR 0 B %d" % params['baudrate'])

    def _sendCmd(self,cmd):
        if self.debug:
            print('cmd: {0}'.format(cmd))
        cmd = '{0}\r'.format(cmd)
        wr = self.write(cmd)
        rsp = self._response()
        return rsp
        
    def _response(self):
        response = [r for r in self.readline()]
        response = response[1:-1]
        print(len(response))
        print(response)
        
        self.status = self.STATUS[response[2]]
        
        return response[3:]

    def setDiameter(self,val):
        """
        Set the syringe inside diameter in mm. Valid diameters range from 
        0.1mm to 50.0mm.
        """
        if val < 0.1 or val > 50.0:
            raise ValueError, 'syringe diameter out of range'
        valStr = float2PumpFormat(val)
        self._sendCmd('DIA {0}'.format(valStr))

    def setRate(self,val,units='UM'):
        """
        Set the pumping rate.  Value must be bewteen 0 and 1000 and 
        units must be 'NS', 'UM', 'MM', 'UH', or 'MH'
        """
        if not units.upper() in ('NS', 'UM', 'MM', 'UH', 'MH'):
            raise ValueError, 'unknown pumping rate units: {0}'.format(units)
        if units.upper() == 'NS':
            val = 60.0*val/(1.0e3)
            units = 'UM'
        valStr = float2PumpFormat(val)
        self._sendCmd('RAT {0} {1}'.format(valStr,units))

    def setDirection(self,val):
        """
        Set the pump direction - infuse 'INF', or withdraw 'WDR'
        """
        val = val.lower()
        if val in ('infuse', 'inf'):
            valStr = 'INF'
        elif val in ('withdraw', 'wdr'):
            valStr = 'WDR'
        self._sendCmd('DIR {0}'.format(valStr))

    def setAccumUnits(self,units):
        """
        Sets the volume units ML or UL - overides the default value set when the 
        syringe diameter is set.
        """
        if not units in ('ML', 'UL'):
            raise ValueError, 'unknown volume unit: {0}'.format(units)
        self._sendCmd('VOL {0}'.format(units))

    def clearVolumeAccum(self,accumType='both'):
        """
        Clears the volume accumlator. If accumType == 'INF' then just the
        infused volume accumulator is cleared. If accumType == 'WDR' then just
        the withdrawn volume accumulator is cleared. If accumType='BOTH' then
        both infused and withdrawn volume accumulators are cleared.   
        """
        accumType = accumType.lower()
        if accumType in ('inf', 'both'):
            self._sendCmd('CLD INF')
        if accumType in ('wdr', 'both'):
            self._sendCmd('CLD WDR')

    def run(self):
        """
        Start the syringe pump. 
        """
        self._sendCmd('RUN')

    def stop(self):
        """
        Stop the syring pump.
        """
        self._sendCmd('STP')

    def getVolumeAccum(self):
        """
        Return the values in the pump volume accumulators. Value is always returned in
        nano liters.
        """
        rsp = self._sendCmd('DIS')
        rsp = [x for x in rsp]

        print(rsp)

        # Get volume units
        units = ''.join(rsp[-2:])
        infuse = float(''.join(rsp[1:5]))
        withdraw = float(''.join(rsp[7:12]))
        print(units)
        
        if units == 'UL':
            scale = 1.0e3
        elif units == 'ML':
            scale = 1.0e6
        else:
            raise IOError, 'unknown volume unit: {0}'.format(units)
        infuse = scale*infuse
        withdraw = scale*withdraw
        return infuse, withdraw
        
    def disconnect(self):
        """
        Stop pump and close serial port.  Automatically called when Python
        exits.
        """
        try:
            self.stop()
        finally:
            self.ser.close()
            return # Don't reraise error conditions, just quit silently
            
    def canCalibrate(self): return False

def float2PumpFormat(val):
    """
    Normalize floating point number into format suitable for sending
    to the syringe pump
    """
    val = float(val)
    if val < 0 or val >=1000:
        raise ValueError, 'value out of range'
    if val >= 100:
        pumpStr = '{0:3.1f}'.format(val)
    elif val >=10:
        pumpStr = '{0:2.2f}'.format(val)
    else:
        pumpStr = '{0:1.3f}'.format(val)
    return pumpStr

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    #if 1:
    dev = NewEraPump("COM6")
    dev.debug = True 
    dev.setDiameter(1.0)
    dev.setRate(2.0,'MH')
    dev.setAccumUnits('UL')
    dev.clearVolumeAccum()
    dev.setDirection('INF')
    infuse, withdraw = dev.getVolumeAccum()
    print('infuse: {0} (nl), withdraw: {1} (nl)'.format(infuse,withdraw))
    dev.run()
    time.sleep(3)
    dev.setDirection('WDR')
    time.sleep(3)
    infuse, withdraw = dev.getVolumeAccum()
    print('infuse: {0} (nl), withdraw: {1} (nl)'.format(infuse,withdraw))
    dev.stop()