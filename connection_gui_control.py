import common

class ConnectionGuiControl(object):
    def __init__(self, ui, scanner_control):
        self.ui = ui
        self.scanner_control = scanner_control

        self.ui.shield_port_combo.addItems(self.scanner_control.shield_control.get_ports())

        self.ui.baud_rate_combo.setCurrentText(str(self.scanner_control.shield_control.get_baud()))

        self.ui.connect_button.clicked.connect(lambda: self.connect())

        self.ui.disconnect_button.setDisabled(True)
        self.ui.disconnect_button.clicked.connect(lambda: self.disconnect())

        self.scanner_control.cron.add_job(0.5, self.update_stats)

    def update_stats(self):
        green_condition = self.scanner_control.shield_control.is_connected() and\
                          self.scanner_control.shield_control.is_ready and\
                          self.scanner_control.shield_control.is_tx_running() and\
                          self.scanner_control.shield_control.is_rx_running() and\
                          self.scanner_control.micro_control.is_connected()
        common.set_ind_condition(self.ui.conn_ind, green_condition)

    def connect(self):
        common.set_ind_yellow(self.ui.conn_ind)
        self.ui.conn_ind.repaint()
        self.scanner_control.shield_control.set_port(self.ui.shield_port_combo.currentText())
        self.scanner_control.shield_control.set_baud(int(self.ui.baud_rate_combo.currentText()))
        self.scanner_control.shield_control.connect()
        self.scanner_control.micro_control.connect(self.ui.micro_index_spin.value(), 0) # Select highest res
        self.ui.connect_button.setDisabled(True)
        self.ui.disconnect_button.setEnabled(True)
        
    def disconnect(self):
        self.scanner_control.shield_control.disconnect()
        self.scanner_control.micro_control.disconnect()
        self.ui.connect_button.setEnabled(True)
        self.ui.disconnect_button.setDisabled(True)
        self.scanner_control.cron.do_cron()