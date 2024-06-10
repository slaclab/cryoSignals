from PyQt5.QtWidgets import QVBoxLayout
from pydm import Display
from pydm.widgets import PyDMArchiverTimePlot


class GlobalCryoDisplay(Display):
    def __init__(self):
        super().__init__()
        base_layout = QVBoxLayout()
        self.setLayout(base_layout)
        self.setWindowTitle("Global Cryo Signals")

        plot = PyDMArchiverTimePlot()
        plot.setShowXGrid(True)
        plot.setShowYGrid(True)
        plot.setPlotTitle("Global Cryo Signals")
        plot.setShowLegend(True)
        plot.setTimeSpan(6000)
        plot.setAutoRangeY(False)

        plot.addAxis(
            name="heater",
            orientation="left",
            label="Total Heater Power",
            min_range=0,
            max_range=4000,
            enable_auto_range=False,
            log_mode=False,
            plot_data_item=None,
        )

        for idx, upper_limit in enumerate([168, 452, 2016, 3360]):
            plot.addAxis(
                name=f"l{idx}b",
                orientation="right",
                label=f"L{idx}B Amplitude",
                min_range=0,
                max_range=upper_limit,
                enable_auto_range=False,
                log_mode=False,
                plot_data_item=None,
            )

        plot.addYChannel(
            useArchiveData=True,
            y_channel="CHTR:CM00:0:HTR_POWER_TOT",
            yAxisName="heater",
        )

        for idx in range(4):
            plot.addYChannel(
                useArchiveData=True,
                y_channel=f"ACCL:L{idx}B:1:AACTMEANSUM",
                yAxisName=f"l{idx}b",
            )

        base_layout.addWidget(plot)
