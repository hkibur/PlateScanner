import serial
import serial.tools.list_ports
import threading
import time
import struct

import packets
import common

TX_WORKER_TIME = 0.1
RX_WORKER_TIME = 0.1
READY_TIMEOUT = 5

class ShieldTxWorker(threading.Thread):
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.packet_queue = []
        self.stop = True

        self.num_packets = 0
        self.num_bytes = 0

    def add_packet(self, packet):
        self.packet_queue.insert(0, packet)

    def close(self):
        self.stop = True
        self.join()

    def start(self):
        self.stop = False
        super().start()

    def is_empty(self):
        return len(self.packet_queue) == 0

    def run(self):
        while not self.stop:
            now = time.time()
            if self.is_empty():
                common.thread_delta_sleep(now, TX_WORKER_TIME)
                continue
            packet_raw = self.packet_queue.pop().get_raw()
            self.serial_port.write(packet_raw)
            self.serial_port.flushInput()
            self.num_packets += 1
            self.num_bytes += len(packet_raw)

            common.thread_delta_sleep(now, TX_WORKER_TIME)
            
class ShieldRxWorker(threading.Thread):
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.packet_queue = []
        self.stop = True

        self.num_packets = 0
        self.num_bytes = 0

    def get_packet(self):
        return self.packet_queue.pop() if not self.is_empty() else None

    def close(self):
        self.stop = True
        self.join()

    def start(self):
        self.stop = False
        super().start()

    def is_empty(self):
        return len(self.packet_queue) == 0

    def run(self):
        while not self.stop:
            now = time.time()
            packet_raw = self.serial_port.readline()
            if len(packet_raw) == 0:
                common.thread_delta_sleep(now, RX_WORKER_TIME)
                continue
            packet = packets.from_packet_type(packet_raw)
            self.packet_queue.insert(0, packet)
            self.num_packets += 1
            self.num_bytes += len(packet_raw)
            common.thread_delta_sleep(now, RX_WORKER_TIME)

class ShieldControl(object):
    def __init__(self):
        self.serial_port = serial.Serial()
        self.serial_port.timeout = RX_WORKER_TIME
        self.serial_port.write_timeout = TX_WORKER_TIME

        self.tx_worker = None
        self.rx_worker = None

        self.is_ready = False

    def write_packet(self, packet):
        self.tx_worker.add_packet(packet)

    def pop_packet(self):
        return self.rx_worker.get_packet()

    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def set_port(self, port):
        self.serial_port.port = port

    def get_baud(self):
        return self.serial_port.baudrate

    def set_baud(self, rate):
        self.serial_port.baudrate = rate

    def connect(self):
        self.serial_port.open()
        self.tx_worker = ShieldTxWorker(self.serial_port)
        self.tx_worker.start()
        self.rx_worker = ShieldRxWorker(self.serial_port)
        self.rx_worker.start()

        start_time = time.time()
        while self.rx_worker.is_empty():
            time.sleep(RX_WORKER_TIME)
            if time.time() - start_time > READY_TIMEOUT:
                print("Ready timeout")
                self.is_ready = False
                return
        packet = self.rx_worker.get_packet()
        self.is_ready = isinstance(packet, packets.ReadyPacket)

    def disconnect(self):
        if self.is_tx_running():
            self.tx_worker.close()
        self.tx_worker = None
        if self.is_rx_running():
            self.rx_worker.close()
        self.rx_worker = None
        if self.is_connected():
            self.serial_port.close()
        self.is_ready = False

    def is_connected(self):
        return self.serial_port.is_open

    def is_tx_running(self):
        return self.tx_worker is not None and not self.tx_worker.stop

    def is_tx_data(self):
        return self.tx_worker is not None and not self.tx_worker.is_empty()

    def is_rx_running(self):
        return self.rx_worker is not None and not self.rx_worker.stop

    def is_rx_data(self):
        return self.rx_worker is not None and not self.rx_worker.is_empty()

    def tx_packet_count(self):
        if self.tx_worker is not None:
            return self.tx_worker.num_packets
        return 0

    def tx_byte_count(self):
        if self.tx_worker is not None:
            return self.tx_worker.num_bytes
        return 0

    def rx_packet_count(self):
        if self.tx_worker is not None:
            return self.rx_worker.num_packets
        return 0

    def rx_byte_count(self):
        if self.rx_worker is not None:
            return self.rx_worker.num_bytes
        return 0