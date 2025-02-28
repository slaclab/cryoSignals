from typing import Dict, List

import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFormLayout, QGridLayout, QVBoxLayout, QWidget
from pydm import Display
from pydm.widgets import PyDMLabel, PyDMTimePlot

from lcls_tools.superconducting.sc_linac import MACHINE, Cryomodule
from lcls_tools.superconducting.sc_linac_utils import L0B, L1B, L1BHL, L2B, L3B


def get_dimensions(options: List[str]):
    num_options = len(options)
    row_count = int(np.sqrt(num_options))
    col_count = int(np.ceil(np.sqrt(num_options)))
    if row_count * col_count != num_options:
        col_count += 1
    return col_count


class CryoReadbacks():
    def __init__(self, cryomodule: Cryomodule):
        super().__init__()
        self.main_layout: QFormLayout = QFormLayout()
        
        for pv in [cryomodule.ds_level_pv, cryomodule.us_level_pv,
                   cryomodule.pv_addr("AACTMEANSUM"),
                   cryomodule.jt_valve_readback_pv]:
            label = PyDMLabel(init_channel=pv)
            label.alarmSensitiveContent = True
            self.main_layout.addRow(pv, label)


class CryoPlot(PyDMTimePlot):
    def __init__(self, cryomodule: Cryomodule):
        super().__init__()
        self.setTimeSpan(600)
        self.showLegend = True
        self.setPlotTitle(f"CM{cryomodule.name}")
        self.setUpdatesAsynchronously(True)
        self.setAutoRangeY(False)
        self.setShowYGrid(True)
        self.setShowXGrid(True)
        
        self.ds_axis = self.addAxis(plot_data_item=None, name="DS Level",
                                    orientation="right",
                                    label="DS Liquid Level (%)", min_range=85, max_range=95,
                                    enable_auto_range=False)
        self.ds_curve = self.addYChannel(y_channel=cryomodule.ds_level_pv, yAxisName="DS Level")
        self.ds_curve.setUpdatesAsynchronously(True)
        
        self.ds_axis = self.addAxis(plot_data_item=None, name="US Level",
                                    orientation="right",
                                    label="US Liquid Level (%)", min_range=60, max_range=80,
                                    enable_auto_range=False)
        self.us_curve = self.addYChannel(y_channel=cryomodule.us_level_pv, yAxisName="US Level")
        self.us_curve.setUpdatesAsynchronously(True)
        
        self.aact_axis = self.addAxis(plot_data_item=None, name="Amplitude Sum",
                                      orientation="right",
                                      label="Amplitude Sum (MV)", min_range=0, max_range=160,
                                      enable_auto_range=False)
        self.aact_curve = self.addYChannel(y_channel=cryomodule.pv_addr("AACTMEANSUM"),
                                           yAxisName="Amplitude Sum")
        self.aact_curve.setUpdatesAsynchronously(True)
        #
        self.jt_axis = self.addAxis(plot_data_item=None, name="JT Position",
                                    orientation="right",
                                    label="JT Position (%)", min_range=0, max_range=100,
                                    enable_auto_range=False)
        self.jt_curve = self.addYChannel(y_channel=cryomodule.jt_valve_readback_pv,
                                         yAxisName="JT Position")
        self.jt_curve.setUpdatesAsynchronously(True)


class CryoSignals(Display):
    def ui_filename(self):
        return "cryoSignals.ui"
    
    def __init__(self, parent=None, args=None):
        super().__init__(parent=parent, args=args)
        
        tab_map: List[QWidget] = [self.ui.l0b_tab, self.ui.l1b_tab,
                                  self.ui.l2b_tab, self.ui.l3b_tab]
        
        self.plots: Dict[str, CryoPlot] = {}
        
        for linac_idx, cryo_list in enumerate([L0B, L1B + L1BHL, L2B, L3B]):
            tab_object = tab_map[linac_idx]
            grid_layout: QGridLayout = QGridLayout()
            tab_object.setLayout(grid_layout)
            
            col_count = get_dimensions(cryo_list)
            
            for cryo_idx, cryo_name in enumerate(cryo_list):
                cm_layout = QVBoxLayout()
                cryomodule = MACHINE.cryomodules[cryo_name]
                cryo_plot = CryoPlot(cryomodule)
                # readbacks = CryoReadbacks(cryomodule).main_layout
                cm_layout.addWidget(cryo_plot)
                # cm_layout.addLayout(readbacks)
                grid_layout.addLayout(cm_layout, int(cryo_idx / col_count),
                                      cryo_idx % col_count)
                self.plots[cryo_name] = cryo_plot
        
        self.ui.minute_spinbox.valueChanged.connect(self.update_timespans)
    
    @pyqtSlot(int)
    def update_timespans(self, minutes: int):
        seconds = minutes * 60
        for plot in self.plots.values():
            plot.setTimeSpan(seconds)
