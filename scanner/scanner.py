import win32file
import win32api
import winerror
import time

import scanner_layout as sl

PORT_PREFIX = "\\\\.\\"
step_packet_name = "step_packet"
PER_BYTE_TIMEOUT_MS = 10

DCB_KEYS = {
"BaudRate":          32, 
"XonLim":            16,
"XoffLim":           16,
"ByteSize":          8,
"Parity":            8,
"StopBits":          8,
"XonChar":          -8, 
"XoffChar":         -8,
"ErrorChar":        -8,
"EofChar":          -8,
"EvtChar":          -8,
"fBinary":           1,
"fParity":           1,
"fOutxCtsFlow":      1,
"fOutxDsrFlow":      1,
"fDtrControl":       2,
"fDsrSensitivity":   1,
"fTXContinueOnXoff": 1,
"fOutX":             1,
"fInX":              1,
"fErrorChar":        8,
"fNull":             1,
"fRtsControl":       2,
"fAbortOnError":     1,
}

class Scanner(object):
    def __init__(self):
        self.scanner_handle = None
        self.scanner_dcb = None
        self.scanner_dcb_object = None

        self.layout_ctx = sl.PacketLayoutContext()

        self.rx_buffer = []
        self.tx_timeout = 5 * 1000
        self.rx_timeout = 5 * 1000 
        self.recv_continue_flag = False
        self.recv_running = False

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

    def set_timeout(self, tx_timeout, rx_timeout):
        MAXDWORD = 0xFFFFFFFF
        timeout_tup = (MAXDWORD, MAXDWORD, rx_timeout, PER_BYTE_TIMEOUT_MS, tx_timeout)
        win32file.SetCommTimeouts(self.scanner_handle, timeout_tup)

    def parse_py_dcb(self, dcb_obj):
        ret_dict = {}
        for key, bit_len in DCB_KEYS.iteritems():
            val = getattr(dcb_obj, key)
            if bit_len < 0: # -1 means it is a character
                val = ord(val)
            ret_dict[key] = val
        return ret_dict

    def read_dcb(self):
        """
        Read scanner DCB configuration.
        """
        if self.scanner_handle is None: raise Exception("Can't read DCB, scanner not bound.")
        self.scanner_dcb_object = win32file.GetCommState(self.scanner_handle)
        self.scanner_dcb = self.parse_py_dcb(self.scanner_dcb_object)

    def write_dcb(self):
        """
        Write scanner DCB configuration.
        """
        if self.scanner_handle is None:     raise Exception("Can't write scanner DCB, scanner not bound.")
        if self.scanner_dcb is None:        raise Exception("Can't write scanner DCB, scanner dcb dict is None.")
        if self.scanner_dcb_object is None: raise Exception("Can't write scanner DCB, scanner dcb object is None")
        for key, val in self.scanner_dcb.iteritems(): 
            if DCB_KEYS[key] < 0:
                val = chr(val)
            setattr(self.scanner_dcb_object, key, val)
        win32file.SetCommState(self.scanner_handle, self.scanner_dcb_object)

    def set_io_buffer_size(self, tx_bytes, rx_bytes):
        """
        Set recommended sizes for COM device tx/rx buffers. Generally, sizes should be slightly bigger than maximum packet size.
        """
        if self.scanner_handle is None: raise Exception("Can't set scanner IO buffer size, scanner not bound.")
        win32file.SetupComm(self.scanner_handle, rx_bytes, tx_bytes)

    def write(self, packet_bytes):
        _, written_len = win32file.WriteFile(self.scanner_handle, packet_bytes)
        if written_len < len(packet_bytes):
            print "Info: Couldn't write full packet. Make sure Tx buffer is large enough"
            time.sleep(0.1)
            self.write(packet_bytes[written_len:])

    def write_packet(self, layout_name, layout_dict):
        self.write(self.layout_ctx.get_bytes(layout_name, layout_dict))

    def read(self, length):
        _, raw = win32file.ReadFile(self.scanner_handle, packet_len)
        return bytearray(raw)

    def read_packet(self):
        frame_type = self.read(1)
        layout_name, layout_length = self.layout_ctx.from_frame(frame_type[0])
        if layout_length == 0:
            return layout_name, {}
        raw = self.read(layout_length)
        return layout_name, self.layout_ctx.get_dict(layout_name, raw)

    def recv_worker(self):
        self.recv_running = True
        self.set_timeout(self.tx_timeout, self.rx_timeout)
        while not self.recv_continue_flag:
            time.sleep(0.5)
        self.recv_continue_flag = False
        self.rx_buffer.append(self.read_packet())
        self.recv_running = False