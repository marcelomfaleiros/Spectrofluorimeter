# encoding: utf-8
# Controla o monocromador Spex 500 via porta GPIB.
# revisão 21/06/2023

import pyvisa as visa
import time

class Spex500():
    '''
    -------------------------------------------------------------------------------------------------------
    Command                  | Host sends                  | Spex Controller sends              
    -------------------------------------------------------------------------------------------------------
    -------------------------------------------------------------------------------------------------------
                                                    Utility commands
    -------------------------------------------------------------------------------------------------------
    -------------------------------------------------------------------------------------------------------
    where am I: "<space>"    | 1. Command                  | 1. Program status      
    ---------------------------------------------------------------------------------------------------
                             | Send "<Space>"              | Receive Nothing if system is hung or;
                             |                             | "*" if autobauding is successful 1st time;
         Example:            |                             | "<escape>"+string if in Terminal mode;
                             |                             | "B" if in BOOT program;
                             |                             | "F" if in Main program 
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    set intelligent mode:    | 1. Command                  | 1. No response at all
           "<248>"           |                             |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "<248>"                | Receive nothing
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    set terminal mode: "<Y>" | 1. Command                  | 1. Confirmation             
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "<Y>"                  | Receive "o"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    start main program:      | 1. Command                  | 1. Confirmation        
         "O2000<Null>"       |                             |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "O2000<Null>"          | Receive "<*>"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    reboot if hung: "<222>"  | 1. Command                  | 1. Nothing             
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "<222>"                | Receive nothing
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    read main version:       | 1. Command                  | 1. Confirmation         
         "<z>"               |                             | 2. MAIN version number                                    
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "<z>"                  | "o"
                             |                             | "V3.3<CR>" or similar response
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    read boot version:       | 1. Command                  | 1. Confirmation         
         "<y>"               |                             | 2. BOOT version number                                    
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "<y>"                  | "o"
                             |                             | "V2.3<CR>" or similar response
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    change IEEE488 address:  | 1. Command                  | 1. Acknowledgement    
         "<E>"               | 2. New address in ASCII HEX |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "E3<Null>"             | Receive "<2>"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
                                                Grating Motor Commands
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor init:  "A"         | 1. Command                            | 1. Confirmation
         timeout = 100 s     |                                       |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "<A>"                            | Receive "o"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor set speed:  "B"    | 1. Command                            | 1. Confirmation
         timeout = 300 ms    | 2. Mono System #              [0]     |
                             | 3. Min Frequency Steps/Sec    [1000]  |
                             | 4. Max Frequency Steps/Sec    [36000] |
                             | 5. Ramp TimeMilliseconds (ms) [3000]  |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "B0,400,800,2000<CR>"            | Receive "o"                                 
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor read speed: "C"    | 1. Command                            | 1. Confirmation 
         timeout = 300 ms    | 2. Mono System #[0..1]                | 2. Min Frequency Steps/Sec
                             |                                       | 3. Max Frequency Steps/Sec
                             |                                       | 4. Ramp TimeMilliseconds (ms)
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "C0<CR>"                         | Receive "o"
                             |                                       | Receive "400,800,2000<CR>" 
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor busy check: "E"    | 1. Command                            | 1. Confirmation  
         timeout = 300 ms    |                                       |                                 
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "E"                              | Receive "o"
                             |                                       | Receive "q" 
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor move relative: "F" | 1. Command                            | 1. Confirmation
         timeout = 300 ms    | 2. Mono System #[0..1]                | 
                             | 3. Steps to Move                      |
    ---------------------------------------------------------------------------------------------------
             Example:            | Send "F0,1000<CR>"                    | Receive "o"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor set position: "G"  | 1. Command                            | 1. Confirmation
         timeout = 300 ms    | 2. Mono System #[0..1]                | 
                             | 3. Mono step position                 |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "G0,1000000<CR>"                 | Receive "o"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor read position: "H" | 1. Command                            | 1. Confirmation  
         timeout = 300 ms    | 2. Mono System #[0..1]                | 2. Motor Step Position
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "H0<CR>"                         | Receive "o"
                             |                                       | Receive "1000000<CR>" 
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor limit status: "K"  | 1. Command                            | 1. Confirmation 
         timeout = 300 ms    |                                       | 2. Motor Limit Status
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "K"                              | Receive "o"
                             |                                       | Receive "0<CR>" 
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    motor stop:   "L"        | 1. Command                            | 1. Confirmation
         timeout = 300 ms    |                                       |
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "L"                              | Receive "o"
    ---------------------------------------------------------------------------------------------------
    mirror exit side: "e"    | 1. Command                            | 1. Confirmation
    ---------------------------------------------------------------------------------------------------
         Example:            | Send "e0"                              | Receive "o"
    ---------------------------------------------------------------------------------------------------
    ---------------------------------------------------------------------------------------------------
    '''   
    
    def __init__(self):
        self.data = ['Spex', 'model 232', 's/n 0289']        
        
    def set_up(self):
        self.rm = visa.ResourceManager()
        self.spex = self.rm.open_resource('GPIB0::2')
        
    def identity(self):        
        self.data.append(self.spex.query("z"))                #read MAIN version number
        self.data.append(self.spex.query("y"))                #read BOOT version number
        return self.data    
 
    def gpib_start_up(self):        
        self.spex.write("222")
        self.spex.write(" ")             #send WHERE AM I command
        respWAI = self.spex.read()       #response will be "B" for BOOT or "F" for MAIN
        if respWAI == "B":
            self.spex.write("O2000" + "")     #send "O2000<null>" - transfer control from BOOT to MAIN program
            self.spex.read()
        time.sleep(0.5)        
        self.spex.write("A")                    #initialize mono
        self.spex.read()
        self.spex.timeout = 30000
       
    def busy_status(self):
        status = self.spex.query("E")
        while status != "oz":                            #while motor busy
            status = self.spex.query("E")                #check motor status                                        
    
    def calibration(self, dsp_wavelength_A):    
        self.spex.write("B0,1000,36000,3000")   #set motor speed
        self.spex.read()
        Gwl = dsp_wavelength_A                  #wavelength (wl) A display
        Ground = round(Gwl * 4000)              #wl to steps conversion
        self.spex.write("G0," + str(Ground))    #setting motor position
        self.spex.read()
  
    def run(self, F):                           #F = target wl
        self.spex.write("H0")                   #motor read position
        time.sleep(0.1)
        Houti = self.spex.read()
        Houticond = Houti[1:len(Houti)]         #motor position without termination character
        Hinti = int(Houticond)                  #convert to integer
        Froundi = round(F * 4000)               #convert target wl to steps
        Fin = Froundi - Hinti                   #compute steps to run
        if Fin < 0:                             #if target wl < current wl
            Fin = Fin - 20000                   #5nm backlash
            self.spex.write("F0," + str(Fin))   #motor move relative
            time.sleep(0.1)
            self.spex.read()
            self.busy_status()                  #motor busy check  
            self.spex.write("F0," + str(20000)) #backlash
            self.spex.read()
            self.busy_status()
        else:
            self.spex.write("F0," + str(Fin))   #if target wl > current wl
            time.sleep(0.1)
            self.spex.read()
            self.busy_status()

    def stop(self):
        self.spex.write("L")
        self.spex.read()
