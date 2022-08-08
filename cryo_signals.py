from typing import Dict, List

import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGridLayout, QWidget
from lcls_tools.superconducting.scLinac import (CRYOMODULE_OBJECTS, Cryomodule,
                                                L0B, L1B, L1BHL, L2B, L3B)
from pydm import Display
from pydm.widgets import PyDMTimePlot


def get_dimensions(options: List[str]):
    num_options = len(options)
    row_count = int(np.sqrt(num_options))
    col_count = int(np.ceil(np.sqrt(num_options)))
    if row_count * col_count != num_options:
        col_count += 1
    return col_count


class CryoPlot(PyDMTimePlot):
    def __init__(self, cryomodule: Cryomodule):
        super().__init__()
        self.setTimeSpan(600)
        self.showLegend = True
        self.setUpdatesAsynchronously(True)
        self.setPlotTitle(f"CM{cryomodule.name}")
        self.addYChannel(y_channel=cryomodule.dsLevelPV,
                         yAxisName="DS Liquid Level (%)").setUpdatesAsynchronously(True)
        self.addYChannel(y_channel=cryomodule.usLevelPV,
                         yAxisName="US Liquid Level (%)").setUpdatesAsynchronously(True)
        self.addYChannel(y_channel=cryomodule.pvPrefix + "AACTMEANSUM",
                         yAxisName="Amplitude (MV)").setUpdatesAsynchronously(True)
        self.addYChannel(y_channel=cryomodule.jtValveReadbackPV,
                         yAxisName="JT (%)").setUpdatesAsynchronously(True)


class CryoSignals(Display):
    def ui_filename(self):
        return "cryoSignals.ui"
    
    def __init__(self, parent=None, args=None):
        super().__init__(parent=parent, args=args)
        
        tab_map: List[QWidget] = [self.ui.l0b_tab, self.ui.l1b_tab,
                                  self.ui.l2b_tab, self.ui.l3b_tab]
        
        self.plots: Dict[CryoPlot] = {}
        
        for linac_idx, cryo_list in enumerate([L0B, L1B + L1BHL, L2B, L3B]):
            tab_object = tab_map[linac_idx]
            grid_layout: QGridLayout = QGridLayout()
            tab_object.setLayout(grid_layout)
            
            col_count = get_dimensions(cryo_list)
            
            for cryo_idx, cryo_name in enumerate(cryo_list):
                cryo_plot = CryoPlot(CRYOMODULE_OBJECTS[cryo_name])
                grid_layout.addWidget(cryo_plot, int(cryo_idx / col_count),
                                      cryo_idx % col_count)
                self.plots[cryo_name] = cryo_plot
        
        self.ui.minute_spinbox.valueChanged.connect(self.update_timespans)
    
    @pyqtSlot(int)
    def update_timespans(self, minutes: int):
        seconds = minutes * 60
        for plot in self.plots.values():
            plot.setTimeSpan(seconds)
