import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "/scanner")
sys.path.append(dir_path + "/GUI")

import scanner
import micro
import scanner_program
import guimain

main_scanner = scanner.Scanner()
main_scanner.bind_port(raw_input("Port: "))

main_micro = micro.Microscope()
main_micro.set_index(0)

prog = scanner_program.Prog(main_scanner, main_micro)

scanner_gui = guimain.ScannerGui(main_scanner, main_micro, "Plate Scanner")