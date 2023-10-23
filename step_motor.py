# -*- coding: utf-8 -*-
# Controla um motor de passo genérico via porta paralela.
# revisão 12/04/2023

from parallel_port import *
import time

class StepMotor(ParallelPort):
    
    '''
    Each step motor needs a sequence of digital steps to be controlled.
    We can set four parallel pins, one for each winding, defined by within the sets:
    
    [2, 3, 4, 5, 6, 7, 8, 9] - address 0x378; or
    [1, 14, 16, 17] - address 0x37f
    
    One revolution is a sequence of steps_per_rev steps.

    Usage
    -----

    import step_motor as sm

    step = sm.StepMotor(0.005, [2, 3, 4, 5], 0x378)

    step.clockwise(200)
    
    '''
       
    def __init__(self, step_time, parallel_pin_set, parallel_address):        
        super().__init__(parallel_address)       
        self.step_time = step_time                                #set pulse_time
        self.parallel_pin_set = parallel_pin_set                  #define pins to control                                     
                     
    def step(self, i):                                            #define one pulse
        super().pin(i)                                            #set pin i HIGH
        time.sleep(self.step_time)                                #pulse time   
                
    def clockwise(self, number_of_steps):                         #execute one step clockwise direction  
        step_number = 0
        reverse_pin_set = list(reversed(self.parallel_pin_set))   #reverse the pin set
        reverse_pin_index = 0
        pin = reverse_pin_set[reverse_pin_index]
        while step_number < number_of_steps:
            self.step(pin)
            step_number += 1
            reverse_pin_index += 1            
            if reverse_pin_index <= 3:
                pin = reverse_pin_set[reverse_pin_index]
            else:
                reverse_pin_index = 0
                pin = reverse_pin_set[reverse_pin_index]
                
    def anticlockwise(self, number_of_steps):
        step_number = 0
        pin_set = self.parallel_pin_set                         #reverse the pin set
        pin_index = 0
        pin = pin_set[pin_index]
        while step_number < number_of_steps:
            self.step(pin)
            step_number += 1
            pin_index += 1            
            if pin_index <= 3:
                pin = pin_set[pin_index]
            else:
                pin_index = 0
                pin = pin_set[pin_index]         
