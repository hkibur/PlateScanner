import Tkinter as tk
import ttk

import scanner

dcb_width = 4 * 2

class ScannerGui(object):
    def __init__(self, scanner_obj, title):
        self.sobj = scanner_obj
        
        self.root = tk.Tk()
        self.root.title(title)
        
        self.root.rowconfigure(0, weight = 1)
        self.root.columnconfigure(0, weight = 1)

        image_frame = tk.LabelFrame(self.root, text = "Microscope View")
        image_frame.grid(row = 0, column = 0, sticky = tk.NSEW)

        control_frame = tk.LabelFrame(self.root, text = "Scanner Control")
        control_frame.grid(row = 0, column = 1, sticky = tk.NSEW)

        setting_frame = tk.LabelFrame(self.root, text = "Settings")
        setting_frame.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW)

        self.error_label = tk.Label(self.root)
        self.error_label.grid(row = 2, column = 0, columnspan = 2, sticky = tk.NSEW)

        sett_notebook = ttk.Notebook(setting_frame)
        sett_notebook.pack(fill = tk.BOTH)

        dcb_sett = tk.Frame(sett_notebook)
        sett_notebook.add(dcb_sett, text = "DCB")

        self.sobj.read_dcb()

        self.var_lookup = {}
        grid_iter = 0
        for key in self.sobj.scanner_dcb.keys():
            self.var_lookup[key] = tk.StringVar()
            tk.Label(dcb_sett, text = key).grid(row = grid_iter // dcb_width, column = grid_iter % dcb_width, sticky = tk.E)
            tk.Entry(dcb_sett, textvariable = self.var_lookup[key], width = 8).grid(row = (grid_iter + 1) // dcb_width, column = (grid_iter + 1) % dcb_width, sticky = tk.W)
            self.var_lookup[key].set("%X" % self.sobj.scanner_dcb[key])
            grid_iter += 2

        tk.Button(dcb_sett, text = "Read", command = self.read_dcb).grid(row = (grid_iter // dcb_width) + 1, column = 0)
        tk.Button(dcb_sett, text = "Write", command = self.write_dcb).grid(row = (grid_iter // dcb_width) + 1, column = 1)

        self.root.mainloop()

    def status_write(self, message):
        self.error_label.config(text = message, fg = "#000000")

    def error_write(self, message):
        self.error_label.config(text = message, fg = "#FF0000")

    def read_dcb(self):
        for key in self.sobj.scanner_dcb.keys():
            self.var_lookup[key].set("%X" % self.sobj.scanner_dcb[key])
        self.status_write("DCB read")

    def write_dcb(self):
        for key, var in self.var_lookup.iteritems():
            val = var.get()
            # Do some validation
            try:
                val = int(val, 16)
            except ValueError:
                self.error_write("%s not valid hex: %s" % (key, val))
                return                
            if val < 0 or val >= (1 << abs(scanner.DCB_KEYS[key])):
                self.error_write("%s out of range 0 to %X: %s" % (key, (1 << abs(scanner.DCB_KEYS[key])) - 1, var.get()))
                return
        
        for key, var in self.var_lookup.iteritems():
            val = int(var.get(), 16)
            self.sobj.scanner_dcb[key] = val

        try:
            self.sobj.write_dcb()   
        except Exception as e:
            self.error_write(e.message)
            return
        self.status_write("DCB written")