# encoding: utf-8
# Controla o monocromador Thermo Jarrell Ash via porta paralela.
# revisão 09/05/2023

import step_motor as sm
import time

class ThermoJarrellAsh():

    '''
    
    Usage:
    
    import thermo_jarrell_ash as tja

    ext_mono = ThermoJarrellAsh(34575)
    ext_mono.start_up(600, 600.05)    

    '''

    sn_6902 = dict([
        ('brand', 'Thermo Jarrell Ash'), 
        ('date', '9/4/90'),
        ('model', '82-415a'),
        ('s/n', '6902'),
        ('step factor', 24),
        ('pin sequence', [6, 7, 8, 9]),
        ('pulse width', 0.004),
        ('step motor', 'MAE HY 200'),
        ('phases', '4'),
        ('current/phase', '1 A / phase'),
        ('steps per revolution', '200 steps/rev')
    ])

    sn_34575 = dict([
        ('brand', 'Thermo Jarrell Ash'), 
        ('date', ''),
        ('model', '82-020'),
        ('s/n', '34575'),
        ('step factor', 120),
        ('pin sequence', [3, 2, 4, 5]),
        ('pulse width', 0.004),
        ('step motor', 'MAE HY 200'),
        ('phases', '4'),
        ('current/phase', '1 A / phase'),
        ('steps per revolution', '200 steps/rev')
    ])    
    
    def __init__(self, serial_number):
        self.serial_number = serial_number
          
    def setup_step_motor(self):
        if self.serial_number == 6902:
            self.step_factor = self.sn_6902['step factor']
            self.excitation_motor = sm.StepMotor(self.sn_6902['pulse width'], self.sn_6902['pin sequence'], 0x378)
        elif self.serial_number == 34575:
            self.step_factor = self.sn_34575['step factor']
            self.excitation_motor = sm.StepMotor(self.sn_34575['pulse width'], self.sn_34575['pin sequence'], 0x378)

    def calibration(self, display_wl, target_wl):
        cal = (target_wl - display_wl) * self.step_factor
        if cal < 0:
            self.excitation_motor.anticlockwise(abs(cal))
            self.backlash()
        elif cal > 0:
            self.excitation_motor.clockwise(cal)
        elif cal == 0:
            pass

    def backlash(self):
        backsteps = 5 * self.step_factor                          #backlash = 5 steps                        
        self.excitation_motor.anticlockwise(backsteps)
        self.excitation_motor.clockwise(backsteps)
            
    def start_up(self, display_wl, spectral_start):
        start = (spectral_start - display_wl) * self.step_factor
        if start < 0:
            self.excitation_motor.anticlockwise(abs(start))
            self.backlash()
        elif start > 0:
            self.excitation_motor.clockwise(start)
        elif start == 0:
            pass
            
    def step_forward(self, spectral_step):
        step = spectral_step * self.step_factor
        self.excitation_motor.clockwise(step)

    def step_backward(self, spectral_step):
        step = spectral_step * self.step_factor
        self.excitation_motor.anticlockwise(step)
        self.backlash()
        
