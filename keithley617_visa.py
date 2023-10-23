# encoding: utf-8
# Controla o eletrômetro Keithley 617 via porta GPIB.
# revisão 19/06/2023

import pyvisa as visa
import serial
import time

class Keithley617():
    
    '''
    - Command = a number of commands grouped together in one string.

    - A command string is terminated with an ASCII "X" character, which tells
      the instrument to execute the command string.
      
    -  Commands sent without the "X" character will not be executed at that time,
       but they will be retained within an internal command buffer for execution
       at the time the "X" character is received.
    
    - If any error occur, the instrument will display appropriate front panel
      error messages and generate an SRQ if programmed to do so.
      
    - To force a particular command sequence, you would follow each command with
      the execute character, as in the example string, ClXZlXCOX, which can be
      used to zero correct the instrument. 

    ----------------------------------------------------------------------------
    Mode                  |  Command  |              Description
    ----------------------------------------------------------------------------
    Execute               |     X     |
    ----------------------------------------------------------------------------  
    Function              |     F0    | Volts 
                          |     F1    | Amps  
                          |     F2    | Ohms 
                          |     F3    | Coulombs
                          |     F4    | External feedback
                          |     F5    | V/I Ohms      
    ----------------------------------------------------------------------------
    Range                 |           | Volts |  Amps |  Ohms | Coulombs   
                          |     R0    | Auto  |  Auto |  Auto | Auto  
                          |     R1    | 200mV |   2pA |   2kΩ | 200pC
                          |     R2    |   2 V |  20pA |  20kΩ |   2nC
                          |     R3    |  20 V | 200pA | 200kΩ |  20nC
                          |     R4    | 200 V |   2nA |   2MΩ |  20nC
                          |     R5    | 200 V |  20nA |  20MΩ |  20nC
                          |     R6    | 200 V | 200nA | 200MΩ |  20nC
                          |     R7    | 200 V |   2uA |   2GΩ |  20nC
                          |     R8    | 200 V |  20uA |  20GΩ |  20nC
                          |     R9    | 200 V | 200uA | 200GΩ |  20nC
                          |     R10   | 200 V |   2mA | 200GΩ |  20nC
                          |     R11   | 200 V |  20mA | 200GΩ |  20nC
                          |     R12   | Cancel autoranging for all functions
    -----------------------------------------------------------------------------  
    Zero Check            |     C0    | Zero Check off 
                          |     C1    | Zero Check on
    -----------------------------------------------------------------------------
    Zero Correct          |     Z0    | Zero correct disabled 
                          |     Z1    | Zero correct enabled
    -----------------------------------------------------------------------------
    Baseline Suppression  |     N0    | baseline suppression disabled  
                          |     N1    | baseline suppression enabled
    -----------------------------------------------------------------------------
    Display mode          |     D0    | Display electrometer 
                          |     D1    | Display voltage source
    ----------------------------------------------------------------------------- 
    Reading mode          |     B0    | Electrometer 
                          |     B1    | Buffer reading
                          |     B2    | Maximum reading 
                          |     B3    | Minimum reading
                          |     B4    | Voltage source
    -----------------------------------------------------------------------------  
    Data Store            |     Q0    | Conversion rate  
                          |     Q1    | One reading per second
                          |     Q2    | One reading every 10 seconds 
                          |     Q3    | One reading per minute
                          |     Q4    | One reading every 10 minutes 
                          |     Q5    | One reading per hour
                          |     Q6    | Trigger mode 
                          |     Q7    | disabled
    -----------------------------------------------------------------------------
    Voltage source        |V+nnn.nn or| Voltage source value: -102.35V to +102.4V,  
    Value                 |V+n.nnnnE+n| 50mV increments
    ----------------------------------------------------------------------------- 
    Voltage source        |     O0    | Source output Off (0V) 
    Operate               |     O1    | Source output On (Programmed Value) 
    -----------------------------------------------------------------------------  
    Calibration value     |A+nnn.nn or| Calibrate function and range  
                          | An.nnnE+n | 
    -----------------------------------------------------------------------------
    Store calibration     |     L1    | Store calibration constants in NVRAM  
    ----------------------------------------------------------------------------- 
    Data format           |     G0    | Reading with prefix (NDCV -1.23456E+00) 
                          |     G1    | Reading without prefix (-1.23456E+00)
                          |     G2    | Reading with prefix and buffer suffix
                          |           | (NDCV-1.23456E+00, 012)
    -----------------------------------------------------------------------------  
    Trigger mode          |     T0    | Continuous, trigger by talk  
                          |     T1    | One-shot, trigger by talk
                          |     T2    | Continuous, trigger by GET 
                          |     T3    | One-shot, trigger by GET
                          |     T4    | Continuous, trigger by X 
                          |     T5    | One-shot, trigger by X
                          |     T6    | Continuous, trigger by external trigger 
                          |     T7    | One-shot, trigger by external trigger
    -----------------------------------------------------------------------------
    SRQ                   |     M0    | Disable SRQ  
                          |     M1    | Reading overflow
                          |     M2    | Buffer full 
                          |     M8    | Reading done
                          |     M16   | Ready 
                          |     M32   | Error
    -----------------------------------------------------------------------------
    EOI and Bus hold off  |     K0    | Enable EOI and bus hold-off on X  
                          |     K1    | Disable EOI, Enable bus hold-off on X
                          |     K2    | Enable EOI, disable bus hold-off on X 
                          |     K3    | Disable both EOI and bus hold-off on X
    -----------------------------------------------------------------------------
    Terminator            | Y(LF CR)  | Terminator = LF CR  
                          | Y(CR LF)  | Terminator = CR LF
                          | Y(ASCII)  | Terminator = ASCII character 
                          |     YX    | No terminator
    -----------------------------------------------------------------------------
    Status word           |    U0     | Send status format: 617 FBBCZNTOBGDOMMKYY  
                          |    U1     | Error conditions
                          |    U2     | Data conditions
    -----------------------------------------------------------------------------

    Usage:
    ------

    import keithley617 as ktl617
    k617 = ktl617.Keithley617()
    k617.comm_setup()

    '''

    function = dict([
        ('Volts', 'F0'),      
        ('Amps','F1'),   
        ('Ohms', 'F2'),      
        ('Coulombs', 'F3'), 
        ('External_feedback', 'F4'), 
        ('V/I Ohms', 'F5')
    ])

    volts_range = dict([
        ('Auto', 'R0'),
        ('200 mV', 'R1'),
        ('2 V', 'R2'),
        ('20 V', 'R3'),
        ('200 V', 'R4'),        
        ('Cancel Autoranging', 'R12')
    ])
    
    amps_range = dict([
        ('Auto', 'R0'),
        ('2 pA', 'R1'), 
        ('20 pA', 'R2'), 
        ('200 pA', 'R3'), 
        ('2 nA', 'R4'), 
        ('20 nA', 'R5'),
        ('200 nA', 'R6'),
        ('2 uA', 'R7'), 
        ('20 uA', 'R8'),
        ('200 uA', 'R9'),
        ('2 mA', 'R10'), 
        ('20 mA', 'R11'),
        ('Cancel Autoranging', 'R12')        
    ])

    ohms_range = dict([
        ('Auto', 'R0'),
        ('2 kΩ', 'R1'), 
        ('20 kΩ', 'R2'), 
        ('200 kΩ', 'R3'), 
        ('2 MΩ', 'R4'), 
        ('20 MΩ', 'R5'),
        ('200 MΩ', 'R6'),
        ('2 GΩ', 'R7'),
        ('20 GΩ', 'R8'),
        ('200 GΩ', 'R9'),   
        ('Cancel Autoranging', 'R12')      
    ])

    coulombs_range = dict([
        ('Auto', 'R0'),
        ('200 pC', 'R1'), 
        ('2 nC', 'R2'), 
        ('20 nC', 'R3'),         
        ('Cancel Autoranging', 'R12')       
    ])

    zero_check = dict([
        ('Off', 'C0'),
        ('On', 'C1')    
    ])

    zero_correct = dict([
        ('Disabled', 'Z0'),
        ('Enabled', 'Z1')
    ])

    baseline_suppression = dict([
        ('Disabled', 'N0'),
        ('Enabled', 'N1')
    ])

    display_mode = dict([
        ('Electrometer', 'D0'),
        ('Voltage source', 'D1')
    ])

    reading_mode = dict([
        ('Electrometer', 'B0'),
        ('Buffer reading', 'B1'),
        ('Maximum reading', 'B2'),
        ('Minimum reading', 'B3'),
        ('Voltage source', 'B4')
    ])

    data_store = dict([
        ('Conversion rate', 'Q0'),
        ('One reading per second', 'Q1'),
        ('One reading every 10 seconds', 'Q2'),
        ('One reading per minute', 'Q3'),
        ('One reading every 10 minutes', 'Q4'),
        ('One reading per hour', 'Q5'),
        ('Trigger mode', 'Q6'),
        ('Disabled', 'Q7')
    ])

    data_format = dict([
        ('With prefix', 'G0'),
        ('Without prefix', 'G1'),
        ('with prefix and buffer suffix', 'G2') 
    ])

    trigger_mode = dict([
        ('Continuous trigger by talk', 'T0'),
        ('One-shot trigger by talk', 'T1'),
        ('Continuous trigger by GET', 'T2'),
        ('One-shot trigger by GET', 'T3'),
        ('Continuous trigger by X', 'T4'),
        ('One-shot trigger by X', 'T5'),
        ('Continuous trigger by external trigger', 'T6'),
        ('One-shot trigger by external trigger', 'T7')
    ])

    srq = dict([
        ('Disable SRQ', 'M0'),
        ('Reading overflow', 'M1'),
        ('Buffer full', 'M2'),
        ('Reading done', 'M8'),
        ('Ready', 'M16'),
        ('Error', 'M32')
    ])

    eoi_and_bus_holdoff = dict([
        ('Enable EOI and bus holdoff_on_X', 'K0'),
        ('Disable EOI Enable bus holdoff on X', 'K1'),
        ('Enable EOI disable bus holdoff on X', 'K2'),
        ('Disable EOI and bus holdoff on X', 'K3')
    ])

    terminator = dict([
        ('LF CR', 'Y(LF CR)'),
        ('CR LF', 'Y(CR LF)'),
        ('ASCII character', 'Y(ASCII)'),
        ('No terminator', 'YX')
    ])

    status_word = dict([
        ('Send status format', 'U0'),
        ('Error conditions', 'U1'),
        ('Data conditions', 'U2')
    ])

    def __init__(self):
        self.brand = 'Keithley'
        self.model = '617'

    def gpib_setup(self):
        self.rm = visa.ResourceManager()
        self.keithley617 = self.rm.open_resource('GPIB0::5')
               
    def start_up_auto_config(self, meter_mode):
        if meter_mode == 'Coulombmeter':
            fct = self.function['Coulombs']
        elif meter_mode == 'Voltmeter':
            fct = self.function['Volts']
        elif meter_mode == 'Ohmmeter':
            fct = self.function['Ohms']
        elif meter_mode == 'Amperemeter':
            fct = self.function['Amps']        
        
        meas_range = self.amps_range['Auto']
        zr_ck_on = self.zero_check['On']
        zr_ck_off = self.zero_check['Off']
        zr_ct_on = self.zero_correct['Enabled']
        zr_ct_off = self.zero_correct['Disabled']
        bsl = self.baseline_suppression['Disabled']
        dmd = self.display_mode['Electrometer']
        rmd = self.reading_mode['Electrometer']
        dst = self.data_store['Disabled']
        dfr = self.data_format['Without prefix']
        tmd = self.trigger_mode['One-shot trigger by X']
        s = self.srq['Disable SRQ']
        eoi_hd = self.eoi_and_bus_holdoff['Enable EOI and bus holdoff_on_X']
        ttr = self.terminator['LF CR']
        swd = self.status_word['Send status format']

        string = fct + meas_range + zr_ck_off + zr_ct_off + bsl + dmd + rmd + dst + dfr + tmd + s + 'X'        
        self.keithley617.write(string)
        
        '''#zero check / zero correct
        self.keithley617.write(zr_ck_on + 'X')
        time.sleep(1)
        self.keithley617.write(zr_ct_on + 'X')
        time.sleep(1)
        self.keithley617.write(zr_ck_off + 'X')
        time.sleep(1)
        self.keithley617.write(meas_range + 'X')
        '''
        
    def status(self):
        pass

    def calibration(self):
        pass

    def run(self):
        y = float(self.keithley617.query('X'))     
        
        return y
