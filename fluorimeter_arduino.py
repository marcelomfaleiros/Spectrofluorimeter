# -*- coding: utf-8 -*-

"""
    Author: Marcelo Meira Faleiros
    State University of Campinas, Brazil
"""

import serial
from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
#from pyqtgraph.Qt import QtWidgets as qtw
import numpy as np
import keyboard
import time

class Spectrofluorimeter(QtWidgets.QMainWindow):
    
    '''
    Arduino Nano

    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uic.loadUi('fluorimeter_interface.ui', self)

        self.algn_exc_wl_lineEdit.setText("300")
        self.algn_emi_wl_lineEdit.setText("200")        
        self.wl_ini_em_lineEdit.setText("400")
        self.wl_fin_em_lineEdit.setText("700")
        self.wl_stp_em_lineEdit.setText("1")
        self.wl_exc_em_lineEdit.setText("300")
        self.wl_ini_ex_lineEdit.setText("200")
        self.wl_fin_ex_lineEdit.setText("400")
        self.wl_stp_ex_lineEdit.setText("2")
        self.wl_emi_ex_lineEdit.setText("550")
        self.spex_display_lineEdit.setText("400")
        self.target_wavelength_lineEdit.setText("410")
                
        self.startup_pushButton.clicked.connect(self.inst_startup)
        self.align_pushButton.clicked.connect(self.sample_alignment)
        self.em_meas_pushButton.clicked.connect(self.emission_spectrum)
        self.exc_meas_pushButton.clicked.connect(self.excitation_spectrum)
        self.em_clean_pushButton.clicked.connect(self.clear)
        self.ex_clean_pushButton.clicked.connect(self.clear)
        self.em_save_pushButton.clicked.connect(self.save)
        self.ex_save_pushButton.clicked.connect(self.save)
        self.em_exit_pushButton.clicked.connect(self.exit)
        self.ex_exit_pushButton.clicked.connect(self.exit)
        self.move_pushButton.clicked.connect(self.mono_control)
        self.startup_pushButton.clicked.connect(self.inst_startup)

    def save(self):
        self.data = self.data.transpose()          
        file_data = qtw.QFileDialog.getSaveFileName()[0]
        np.savetxt(file_data, self.data)

    def wl_calibration(self):
        pass

    def mono_control(self):
        target = float(self.target_wavelength_lineEdit.text())
        steps = round((target - self.spex_display) * 500)

        command = f'{steps}\r\n'
        self.arduino.write(command.encode())

        self.spex_display = float(self.target_wavelength_lineEdit.text())

        
    def inst_startup(self):
        self.arduino = serial.Serial(timeout=10)
        self.arduino.port = 'COM4'		
        self.arduino.baudrate = 9600
        self.arduino.open()  
        time.sleep(2)

        #calibrate spex
        self.spex_display = float(self.spex_display_lineEdit.text())
        time.sleep(0.1)

    def graph_start(self):
        self.clear()
        
        self.wl_array = []
        self.pl_array = []
        
        self.graphicsView.showGrid(x=True, y=True, alpha=True)
        self.graphicsView.setLabel("left", "PMT current", units="A")
        self.graphicsView.setLabel("bottom", "Wavelength", units="nm")

        self.dataset = self.graphicsView.plot(self.wl_array, self.pl_array)
        
    def sample_alignment(self):
        #1 - graph startup
        self.graph_start()
        
        #2 - excitation wavelength
        '''self.algn_exc_target = float(self.strt_algn_exc_wl_lineEdit.text())
        delta_exc = self.algn_exc_target - self.strt_exc_wl
        if delta_exc < 0:
            exc_mono.step_backward(abs(delta_exc))
        elif delta_exc > 0:
            exc_mono.step_forward(abs(delta_exc))
        '''
        
        #3 - emission wavelength
        self.algn_emi_target = float(self.strt_algn_emi_wl_lineEdit.text())
        #serial arduino command to send monochromator to target

        #4 - acquire data from electronics
        t = 0
        while True:
            if keyboard.is_pressed('Escape'):
                break            
            #y = self.keithley.run()
            #y = -1*y
            self.wl_array = np.append(self.wl_array, t)
            self.pl_array = np.append(self.pl_array, y)
            self.dataset.setData(self.wl_array, self.pl_array, pen=None, symbol='x')
            pg.Qt.QtWidgets.QApplication.processEvents()

            t += 1

    def emission_spectrum(self):
        self.graph_start()        
        
        self.ini_emi_wl = float(self.wl_ini_em_lineEdit.text())
        self.fin_emi_wl = float(self.wl_fin_em_lineEdit.text())
        self.stp_emi_wl = float(self.wl_stp_em_lineEdit.text())

        x = self.ini_emi_wl
        y = 0
        
        while x <= self.fin_emi_wl:
            if keyboard.is_pressed('Escape'):
                break
            self.emi_mono.run(x)    
            y = self.keithley.run()
            y = -1*y
            self.pl_array = np.append(self.pl_array, y)
            self.wl_array = np.append(self.wl_array, x)
            self.dataset.setData(self.wl_array, self.pl_array, pen=None, symbol='o')

            x += self.stp_emi_wl

            pg.Qt.QtWidgets.QApplication.processEvents()

        data_array = self.wl_array, self.pl_array
        self.data = np.vstack(data_array)
        
    def excitation_spectrum(self):
        #do---->
        #        1 - emission wavelength
        #        2 - excitation wavelength start
        #        3 - measure Keithley current
        #        4 - plot current x wavelength
        #        5 - excitation wavelength step
        #until->
        #        6 - excitation wavelength = excitation wavelength stop
        pass

    def clear(self):
        self.graphicsView.clear()
        
    def exit(self):
        self.close()
        self.arduino.close()
        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    tela = Spectrofluorimeter()
    tela.show()
    app.exec_()
