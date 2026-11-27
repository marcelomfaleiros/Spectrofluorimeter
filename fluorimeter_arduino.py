# -*- coding: utf-8 -*-

"""
    Author: Marcelo Meira Faleiros
    State University of Campinas, Brazil

    Revision - 26/11/26
"""

import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, uic
import pyqtgraph as pg
import numpy as np
import keyboard
import time

class Toast(QtWidgets.QWidget):
    def __init__(self, parent=None, texto="", timeout=3000):
        super().__init__(parent)

        self.setWindowFlags(
            QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(texto)
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
            }
        """)

        container = QtWidgets.QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        c_layout = QtWidgets.QVBoxLayout(container)
        c_layout.addWidget(label)

        layout.addWidget(container)

        self.adjustSize()
        self.opacity = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)

        self.anim = QtCore.QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)

        self.anim.start()

        QtCore.QTimer.singleShot(timeout, self.fade_out)

    def show_(self):
        if self.parent():
            geo = self.parent().geometry()
            x = geo.x() + geo.width() - self.width() - 200
            y = geo.y() + geo.height() - self.height() - 150
            self.move(x, y)

        self.show()

    def fade_out(self):
        self.anim = QtCore.QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.close)
        self.anim.start()

class Spectrofluorimeter(QtWidgets.QMainWindow):
    
    '''
    Arduino Nano

    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uic.loadUi('fluorimeter_interface.ui', self)

        self.steps_per_nm = 500
        self.backlash_steps = 400   # Compensação de backlash (ajustável)
        self.last_direction = 0    # 0: indefinido; +1: avanço; -1: retorno

        self.listar_portas()

        self.algn_exc_wl_lineEdit.setText("300")
        self.algn_emi_wl_lineEdit.setText("400")        
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
        self.calibrate_wavelength_lineEdit.setText("410")
                
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
        self.move_pushButton.clicked.connect(self.move_to_target)
        self.startup_pushButton.clicked.connect(self.inst_startup)
        self.calibrate_pushButton.clicked.connect(self.wl_calibrate)

    def toast(self, texto, timeout=3000):
        self._toast = Toast(self, texto, timeout)
        self._toast.show_()

    def listar_portas(self):

        self.comboBox.clear()

        portas = serial.tools.list_ports.comports()

        for porta in portas:
            self.comboBox.addItem(porta.device)

    def save(self):
        self.data = self.data.transpose()          
        file_data = QtWidgets.QFileDialog.getSaveFileName()[0]
        np.savetxt(file_data, self.data)

    def wl_calibrate(self):
        self.spex_display = self.calibrate_wavelength_lineEdit.text()

    def inst_startup(self): 
        comm_port = self.comboBox.currentText()     
        self.arduino = serial.Serial()
        self.arduino.port = comm_port
        self.arduino.baudrate = 9600
        self.timeout = 0.1
        self.arduino.open()

        # Aguarda inicialização do Arduino
        self.toast("Aguarde: arduino inicializando", 2000)

        porta = self.comboBox.currentText()

        # Calibração inicial do espectrômetro
        self.spex_display = float(self.spex_display_lineEdit.text())
        
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

    def motor_busy(self, timeout=15.0):
        inicio = time.monotonic()

        while time.monotonic() - inicio < timeout:
            if self.arduino.in_waiting:
                resposta = self.arduino.readline().decode(
                "utf-8", errors="ignore"    
                ).strip()

                if resposta:
                    print(f"Arduino: {resposta}")  # diagnóstico

                    if resposta == "DONE":
                        return True
                    elif resposta == "LIMIT":
                        print("Fim de curso atingido")
                    elif resposta == "ZERO":
                        print("Motor desenergizado")

        raise TimeoutError("Arduino não confirmou a conclusão do movimento.")

    def mono_control(self, target):

        steps = round((target - self.spex_display) * self.steps_per_nm)

        if steps == 0:
            return

        direction = 1 if steps > 0 else -1
        invert = self.last_direction != 0 and direction != self.last_direction

        if invert:
            # Ultrapassa o alvo para compensar a folga
            self.arduino.write(f'{steps + direction*self.backlash_steps}\r\n'.encode())
            self.motor_busy(5 + abs(steps + direction*self.backlash_steps)*0.005)

            # Retorna ao alvo pela direção desejada
            self.arduino.write(f'{-direction*self.backlash_steps}\r\n'.encode())
            self.motor_busy(5 + self.backlash_steps*0.005)

        else:
            self.arduino.write(f'{steps}\r\n'.encode())
            self.motor_busy(5 + abs(steps)*0.005)

        self.last_direction = direction
        self.spex_display = target

    def move_to_target(self):
        try:
            wavelength = float(self.target_wavelength_lineEdit.text())
            self.mono_control(wavelength)

        except ValueError:
            print("Comprimento de onda inválido.")

    def gaussian(self, x, A=1, mu=0, sigma=1):
        return A * np.exp(-((np.array(x) - mu)**2) / (2 * sigma**2))

    def emission_spectrum(self):
        self.graph_start()        
        
        self.ini_emi_wl = float(self.wl_ini_em_lineEdit.text())
        self.fin_emi_wl = float(self.wl_fin_em_lineEdit.text())
        self.stp_emi_wl = float(self.wl_stp_em_lineEdit.text())

        mu_gaussiana = (self.fin_emi_wl + self.ini_emi_wl)/2

        x_array = np.arange(self.ini_emi_wl, (self.fin_emi_wl+self.stp_emi_wl), self.stp_emi_wl)
        y_array = self.gaussian(x_array, A=(self.fin_emi_wl+self.stp_emi_wl), mu=mu_gaussiana, sigma=20)

        x = self.ini_emi_wl
        y = 0
        
        while x <= self.fin_emi_wl:
            if keyboard.is_pressed('Escape'):
                break
            self.mono_control(x) 
            time.sleep(1)
            y = y_array[np.argmin(np.abs(x_array - x))]
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
        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    tela = Spectrofluorimeter()
    tela.show()
    app.exec_()