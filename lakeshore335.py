# encoding: utf-8
# Controla o controlador de temperatura LakeShore 335 via porta GPIB.
# revisão 27/01/2023

import pyvisa as visa

class LakeShore():
    '''

       https://www.lakeshore.com/docs/default-source/product-downloads/
       335_manual.pdf?sfvrsn=9f5c5b7f_7
       
       Interface commands:
       -------------------
       *       Begins common interface command
       ?       Required to identify queries
       s[n]    String of alphanumeric characters with length “n.” Send these strings
               using surrounding quotes. Quotes enable characters such as commas
               and spaces to be used without the instrument interpreting them as
               delimiters.
       nn…     String of number characters that may include a decimal point.
       dd      Dotted decimal format, common with IP addresses. Always contains 4
               dot separated 3-digit decimal numbers, such as 192.168.000.012.
       [term]  Terminator characters
       <…>     Indicates a parameter field, many are command specific.
       <state> Parameter field with only On/Off or Enable/Disable states.
       <value> Floating point values have varying resolution depending on the type
               of command or query issued.
               
       Command   |                Function                  |                Usage
       ----------|------------------------------------------|-------------------------------------------------
       *CLS      |  Clear Interface                         | *CLS[term]  
       *ESE      |  Event Status Enable Register            | *ESE <bit weighting>[term]
       *ESE?     |  Event Status Enable Register Query      | *ESE?[term]
       *ESR?     |  Standard Event Status Register Query    | *ESR?[term]
       *IDN?     |  Identification Query                    | *IDN?[term] 
       *OPC      |  Operation Complete                      | *OPC[term] 
       *OPC?     |  Operation Complete Query                | *OPC?[term]
       *RST      |  Reset Instrument                        | *RST[term]   
       *SRE      |  Service Request Enable Register         | *SRE <bit weighting>[term] 
       *SRE?     |  Service Request Enable Register Query   | *SRE?[term] 
       *STB?     |  Status Byte Query                       | *STB?[term]          
       *TST?     |  Self-Test Query                         | *TST?[term]
       *WAI      |  Wait-to-Continue                        | *WAI[term]
       ALARM     |  Input Alarm Parameter                   | ALARM <input>,<off/on>,<high value>,<low value>,
                 |                                          |       <deadband>,<latch enable>,
                 |                                          |       <audible>,<visible> [term]
       ALARM?    |  Input Alarm Parameter Query             | ALARM? <input>[term]
       ALARMST?  |  Input Alarm Status Query                | ALARMST? <input>[term]
       ALMRST    |  Reset Alarm Status                      | ALMRST[term]
       ANALOG    |  Monitor Out Parameter                   | ANALOG <output>,<input>,<units>,<high value>,
                 |                                          |        <low value>,<polarity>[term]
       ANALOG?   |  Monitor Out Parameter Query             | ANALOG? <output>[term]
       ATUNE     |  Autotune                                | ATUNE <output>,<mode>,[term]
       BRIGT     |  Display Brightness                      | BRIGT <brightness value>[term]
       BRIGT?    |  Display Brightness Query                | BRIGT?[term]
       CRDG?     |  Celsius Reading Query                   | CRDG? <input>[term]
       CRVDEL    |  Curve Delete                            | CRVDEL <curve>[term]
       CRVHDR    |  Curve Header                            | CRVHDR <curve>,<name>,<SN>,<format>,<limit value>,
                 |                                          |        <coefficient>[term]
       CRVHDR?   |  Curve Header Query                      | CRVHDR? <curve>[term]
       CRVPT     |  Curve Data Point                        | CRVPT <curve>,<index>,<units value>,
                 |                                          |       <temp value>[term]
       CRVPT?    |  Curve Data Point Query                  | CRVPT? <curve>,<index>[term]
       DFLT      |  Factory Defaults                        | DFLT 99[term]
       DIOCUR    |  Diode Excitation Current Parameter      | DIOCUR <input>,<excitation>[term]
       DIOCUR?   |  Diode Exc. Current Parameter Query      | DIOCUR? <input>[term]
       DISPFLD   |  Custom ModeDisplay Field                | DISPFLD <field>,<source>,<units>[term]
       DISPFLD?  |  Custom Mode Display Field Query         | DISPFLD? <field>[term]
       DISPLAY   |  Display Setup                           | DISPLAY <mode>[term]
       DISPLAY?  |  Display Setup Query                     | DISPLAY?[term]
       EMUL      |  Model 331/332 Emulation Mode            | EMUL <emulation mode>,<PID scaling mode>[term]
       EMUL?     |  Model 331/332 Emulation Mode Query      | EMUL? [term]
       FILTER    |  Input Filter Parameter                  | FILTER <input>,<off/on>,<points>,<window>[term]
       FILTER?   |  Input Filter Parameter Query            | FILTER? <input>[term]
       HTR?      |  Heater Output Query                     | HTR? <output>[term]
       HTRSET    |  Heater Setup                            | HTRSET <output>,<type>,<heater resistance>,
                 |                                          |        <max current>,<max user current>,
                 |                                          |        <current/power>[term]
       HTRSET?   |  Heater Setup Query                      | HTRSET? <output>[term]
       HTRST?    |  Heater Status Query                     | HTRST? <output>[term]
       IEEE      |  IEEE-488 Parameter                      | IEEE <address>[term]
       IEEE?     |  IEEE-488 Interface Parameter Query      | IEEE?[term]
       INCRV     |  Input Curve Number                      | INCRV <input>,<curve number>[term]
       INCRV?    |  Input Curve Number Query                | INCRV? <input>[term]
       INNAME    |  Sensor Input Name                       | INNAME <input>,<name>[term]
       INNAME?   |  Sensor Input Name Query                 | INNAME? <input>[term]
       INTYPE    |  Input Type Parameter                    | INTYPE <input>,<sensor type>,<autorange>,
                 |                                          |        <range>,<compensation>,<units> [term]
       INTYPE?   |  Input Type Parameter Query              | INTYPE? <input>[term]
       KRDG?     |  Kelvin Reading Query                    | KRDG? <input>[term]
       LEDS      |  Front Panel LEDS                        | LEDS <off/on>[term]
       LEDS?     |  Front Panel LEDS Query                  | LEDS?[term]
       LOCK      |  Front Panel Keyboard Lock               | LOCK <state>,<code>[term]
       LOCK?     |  Front Panel Keyboard Lock Query         | LOCK?[term]
       MDAT?     |  Minimum/Maximum Data Query              | MDAT? <input>[term]
       MNMXRST   |  Minimum and Maximum Function Reset      | MNMXRST[term]
       MODE      |  Remote Interface Mode                   | MODE <mode>[term]
       MODE?     |  Remote Interface Mode Query             | MODE?[term]
       MOUT      |  Manual Output                           | MOUT <output>,<value>[term]
       MOUT?     |  Manual Output Query                     | MOUT? <output>[term]
       OPST?     |  Operational Status Query                | OPST? [term]
       OPSTE     |  Operation Status Enable                 | OPSTE <bit weighting> [term]
       OPSTE?    |  Operational Status Enable Query         | OPSTE?[term]
       OPSTR?    |  Opertional Status Register Query        | OPSTR? [term]
       OUTMODE   |  Output Mode                             | OUTMODE <output>,<mode>,<input>,
                 |                                          |         <powerup enable>[term]
       OUTMODE?  |  Output Mode Query                       | OUTMODE? <output>[term]
       POLARITY  |  Output Voltage Polarity Command         | PID <output>,<P value>,<I value>,<D value>[term]
       POLARITY? |  Output Voltage Polarity Query           | PID? <output>[term]
       PID       |  Control Loop PID Values                 | POLARITY <output>,<polarity>[term]
       PID?      |  Control Loop PID Values Query           | POLARITY?[term]
       RAMP      |  Control Setpoint Ramp Parameter         | RAMP <output>,<off/on>,<rate value>[term]
       RAMP?     |  Control Setpoint Ramp Parameter Query   | RAMP? <output>[term]
       RAMPST?   |  Control Setpoint Ramp Status Query      | RAMPST? <output>[term]
       RANGE     |  Heater Range                            | RANGE <output>,<range>[term]
       RANGE?    |  Heater Range Query                      | RANGE? <output>[term]
       RDGST?    |  Input Reading Status Query              | RDGST? <input>[term]
       RELAY     |  Relay Control Parameter                 | RELAY <relay number>,<mode>,<input alarm>,
                 |                                          |       <alarm type>[term]
       RELAY?    |  Relay Control Parameter Query           | RELAY? <relay number>[term]
       RELAYST?  |  Relay Status Query                      | RELAYST? <relay number>[term]
       SCAL      |  Generate SoftCal Curve                  | SCAL <std>,<dest>,<SN>,<T1 value>,<U1 value>,
                 |                                          |      <T2 value>,<U2 value>,<T3 value>,
                 |                                          |      <U3 value>[term]
       SETP      |  Control Setpoint                        | SETP <output>,<value>[term]
       SETP?     |  Control Setpoint Query                  | SETP? <output>[term]
       SRDG?     |  Sensor Units Input Reading Query        | SRDG? <input>[term]
       TEMP?     |  Thermocouple Junction Temperature Query | TEMP?[term]
       TLIMIT    |  Temperature Limit                       | TLIMIT <input>,<limit>[term]
       TLIMIT?   |  Temperature Limit Query                 | TLIMIT? <input>[term]
       TUNEST?   |  Control Tuning Status Query             | TUNEST?[term]
       WARMUP    |  Warmup Supply Parameter                 | WARMUP <output>,<control>,<percentage>[term]
       WARMUP?   |  Warmup Supply Parameter Query           | WARMUP? <output>[term]
       ZONE      |  Control Loop Zone Table Parameter       | ZONE <output>,<zone>,<upper bound>,<P value>,
                 |                                          |      <I value>,<D value>,<mout value>,<range>,
                 |                                          |      <input>,<rate>[term]
       ZONE?     |  Output Zone Table Parameter Query       | ZONE? <output>,<zone>[term]
       ------------------------------------------------------------------------------------------------------
    '''
    def __init__(self):
        self.brand = 'Lakeshore'
        self.model = '335'        
        
    def gpib_set_up(self):
        self.rm = visa.ResourceManager()
        self.lakeshore335 = self.rm.open_resource('GPIB0::10')
        self.lakeshore335.write('*RST')        
        self.lakeshore335.write_termination = '\r\n'
        self.lakeshore335.read_termination = '\r\n'

    def temperature_check(self):
        self.lakeshore335.write('SETP? 1')
        Tsp = float(self.lakeshore335.read())
        roundTsp = round(Tsp, 1)
        self.lakeshore335.write('KRDG? B')
        T = float(self.lakeshore335.read())
        roundT = round(T, 1)
        while abs(roundTsp - roundT) > 0.1:
            self.lakeshore335.write('KRDG? B')
            T = float(self.lakeshore335.read())
            roundT = round(T) 

    def start_up(self):
        self.lakeshore335.write('*CLS')
        self.lakeshore335.write('INNAME A,Control')
        self.lakeshore335.write('INNAME B,Sample')

    def setpoint(self, sp):
        sp = str(sp)
        self.lakeshore335.write('SETP 1,' + sp)

    def heater_range(self, hrg):
        hrg_list = dict([
            ('Off', '0'),
            ('Low', '1'),
            ('Medium', '2'),
            ('High', '3')
        ])
        self.lakeshore335.write('RANGE 1,' + hrg_list[hrg])
