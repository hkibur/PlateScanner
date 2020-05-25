import common

class MovementGuiControl(object):
    def __init__(self, ui, scanner_control):
        self.ui = ui
        self.scanner_control = scanner_control

        self.scanner_control.cron.add_job(0.5, self.update_stats)

    def update_stats(self):
        sc = self.scanner_control.shield_control
        common.set_ind_condition(self.ui.connected_ind, sc.is_connected())
        common.set_ind_condition(self.ui.ready_ind, sc.is_ready)
        common.set_ind_condition(self.ui.tx_running_ind, sc.is_tx_running())
        common.set_ind_condition(self.ui.rx_running_ind, sc.is_rx_running())
        common.set_ind_threeway(self.ui.tx_data_ind, sc.is_tx_running(), sc.is_tx_data())
        common.set_ind_threeway(self.ui.rx_data_ind, sc.is_rx_running(), sc.is_rx_data())
        self.ui.tx_packet_stat.setText(str(sc.tx_packet_count()))
        self.ui.tx_byte_stat.setText(str(sc.tx_byte_count()))
        self.ui.rx_packet_stat.setText(str(sc.rx_packet_count()))
        self.ui.rx_byte_stat.setText(str(sc.rx_byte_count()))