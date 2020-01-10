import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "/scanner")
sys.path.append(dir_path + "/GUI")

import scanner
import guimain

main_scanner = scanner.Scanner()
main_scanner.bind_port(raw_input("Port: "))

scanner_gui = guimain.ScannerGui(main_scanner, "Plate Scanner")