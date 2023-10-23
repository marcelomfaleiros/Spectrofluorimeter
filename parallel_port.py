# -*- coding: utf-8 -*-
# revisão 10/05/2023

from ctypes import windll
import time

class ParallelPort():
    
    '''
    Parallel Data Pins

    Usage with inpout32.dll library:

             (0x378, n) or (0x37a, n): (ADDRESS, DECIMAL) 

    Example: (0x378, 0): channels 2 - 9 at low level
             (0x378, 1): channel 2 at high level and channels 3 - 9 at low level
             (0x378, 255): channels 2 - 9 at high level

             Complete map of parallel DATA and CONTROL pins:

    Adress 0x378 - DATA pins
    ----------------------------------------------
    dec \ pin  | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 |   
    ----------------------------------------------    
        0      | L | L | L | L | L | L | L | L | 
        1      | L | L | L | L | L | L | L | H | 
        2      | L | L | L | L | L | L | H | L | 
        4      | L | L | L | L | L | H | L | L |
        8      | L | L | L | L | H | L | L | L | 
        16     | L | L | L | H | L | L | L | L | 
        32     | L | L | H | L | L | L | L | L | 
        64     | L | H | L | L | L | L | L | L | 
        128    | H | L | L | L | L | L | L | L | 
        255    | H | H | H | H | H | H | H | H | 
        ----------------------------------------------

    Adress 0x37f - CONTROL pins
    -------------------------------------------
    dec \ pin  |  1  |  14  |  16  |  17  |
    -------------------------------------------
        0      |  H  |   H  |   L  |   H  | 
        1      |  L  |   H  |   L  |   H  |
        2      |  H  |   L  |   L  |   H  | 
        3      |  L  |   L  |   L  |   H  | 
        4      |  H  |   H  |   H  |   H  |  
        5      |  L  |   H  |   H  |   H  |  
        6      |  H  |   L  |   H  |   H  | 
        7      |  L  |   L  |   H  |   H  |  
        8      |  H  |   H  |   L  |   L  | 
        9      |  L  |   H  |   L  |   L  | 
        10     |  H  |   L  |   L  |   L  |  
        11     |  L  |   L  |   L  |   L  | 
        12     |  H  |   H  |   H  |   L  |  
        13     |  L  |   H  |   H  |   L  |
        14     |  H  |   L  |   H  |   L  | 
        15     |  L  |   L  |   H  |   L  |
    -------------------------------------------

    Obs: Addresses 0x378 and 0x37f may vary from computer to computer, check at:
        
    System->Hardware->Device Manager->Ports->ECP Printer Port->Properties->Resources

    Using a offboard LPT I got Addresses ExC00 and ExC07.        
  
    For a modern Windows system (i.e., 64-bit), you’ll need to:

    1. Download the latest “binaries” archive from the InpOut32 site
    2. Extract the files
    3. Run the Win32\InstallDriver.exe file (even though it’s in the Win32 directory)
    4. Rename the 64-bit file inpoutx64.dll to inpout32.dll
    5. Place this file in C:\Windows\System32\
    6. Use the Device Manager to get the parallel port address, e.g. 0x378 or 0xCFF4,
        and set this as TRIGGER_ADDRESS in the config.
    (Source: https://labsn.github.io/expyfun/parallel_installation.html)


    Usage
    -----

    import parallel_port as pp
    parallel = pp.ParallelPort(ADDRESS)

    parallel.pin(pin_to_activate)
    
    '''   

    pin_set_0x378 = [2, 3, 4, 5, 6, 7, 8, 9]   #parallel DATA pins 
    pin_set_0x37f = [1, 14, 16, 17]            #parallel CONTROL pins
    dec_0x378 = [1, 2, 4, 8, 16, 32, 64, 128]  #DECIMAL to activate the DATA pins
    dec_0x37f = [10, 9, 15, 13]                #DECIMAL to activate the CONTROL pins
    setpin_command = windll.inpout32.Out32     #command to activate the pin
    
    def __init__(self, address):
        self.address = address                        #parallel port ADDRESS
        
    def all_pin_low(self):                            #set all pins LOW state
        if self.address == 0x378:                     #if DATA pins setted
            self.setpin(self.address, 0)
        else:                                         #if CONTROL pins setted
            self.setpin(self.address, 11)

    def all_pin_high(self):                           #set all pins HIGH state
        if self.address == 0x378:                     #if DATA pins setted
            self.setpin_command(self.address, 255)
        else:                                         #if CONTROL pins setted
            self.setpin_command(self.address, 4)
        
    def pin(self, pin_number):                                 #set specific pin HIGH                                        
        if self.address == 0x378:
            dec_index = self.pin_set_0x378.index(pin_number )  #set DECIMAL to activate pin
            H = self.dec_0x378[dec_index]
            self.setpin_command(self.address, H)
        else:
            dec_index = self.pin_set_0x37f.index(pin_number )  #set DECIMAL to activate pin
            H = self.dec_0x37f[dec_index]
            self.setpin_command(self.address, H)               #activate pin
