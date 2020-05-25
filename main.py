import sys
from PyQt5 import QtWidgets as qt_widget

import main_gui
import scanner_control
import connection_gui_control as cgc
import move_gui_control as mgc
import micro_gui_control as migc
import scanner_gui_control as sgc

gui_app = qt_widget.QApplication([])
gui_main_widget = qt_widget.QMainWindow()
gui_main_window = main_gui.Ui_main_window()
gui_main_window.setupUi(gui_main_widget)

scanner_control = scanner_control.ScannerControl()

cgc.ConnectionGuiControl(gui_main_window, scanner_control)
mgc.MovementGuiControl(gui_main_window, scanner_control)
migc.MicroGuiControl(gui_main_window, scanner_control)
a = sgc.ScannerGuiControl(gui_main_window, scanner_control)

scanner_control.cron.start()
gui_main_widget.show()
gui_app.exec_()
scanner_control.close()