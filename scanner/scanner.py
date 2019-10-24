import win32file
import win32api

import scanner_layout as sl

PORT_PREFIX = "\\\\.\\"

class Scanner(object):
    def __init__(self):
        self.scanner_handle = None
        self.scanner_dcb = None
        self.scanner_dcb_object = None

        self.layout_ctx = sl.PacketLayoutContext()

    def bind_port(self, port):
        """
        Bind Scanner object to port, creating a new handle.
        """
        if self.scanner_handle is not None: self.scanner_handle.close()
        self.scanner_handle = win32file.CreateFile(PORT_PREFIX + port,
                                                   win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                                   0,
                                                   None,
                                                   win32file.OPEN_EXISTING,
                                                   0,
                                                   None)
        if self.scanner_handle == win32file.INVALID_HANDLE_VALUE: raise Exception("Creating handle to scanner port failed: %d" % (win32api.GetLastError()))

    def bind_layout(self, filepath):
        """
        Bind packet layout to scanner.
        """
        self.layout_ctx.configure_from_file(filepath)

    def read_dcb(self):
        """
        Read scanner DCB configuration.
        """
        if self.scanner_handle is None: raise Exception("Can't read DCB, scanner not bound.")
        self.scanner_dcb_object = win32file.GetCommState(self.scanner_handle)
        self.scanner_dcb = {key: val for key, val in self.scanner_dcb_object.__dict__.iteritems()}

    def write_dcb(self):
        """
        Write scanner DCB configuration.
        """
        if self.scanner_handle is None:     raise Exception("Can't write scanner DCB, scanner not bound.")
        if self.scanner_dcb is None:        raise Exception("Can't write scanner DCB, scanner dcb dict is None.")
        if self.scanner_dcb_object is None: raise Exception("Can't write scanner DCB, scanner dcb object is None")
        for key, val in self.scanner_dcb.iteritems(): setattr(self.scanner_dcb_object, key, val)
        win32file.SetCommState(self.scanner_handle, self.scanner_dcb_object)

    def set_io_buffer_size(self, tx_bytes, rx_bytes):
        """
        Set recommended sizes for COM device tx/rx buffers. Generally, sizes should be slightly bigger than maximum packet size.
        """
        if self.scanner_handle is None: raise Exception("Can't set scanner IO buffer size, scanner not bound.")
        win32file.SetupComm(self.scanner_handle, rx_bytes, tx_bytes)