import pathlib
import sys
from random import randint
from unittest import TestCase
from unittest.mock import MagicMock

from PyQt5.QtWidgets import QApplication

from cryo_signals import CryoSignals

app = QApplication(sys.argv)


class TestCryoSignals(TestCase):

    def tearDown(self) -> None:
        app.closeAllWindows()

    def test_ui_filename(self):
        display = CryoSignals()
        path = display.ui_filename()
        if not pathlib.Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))

    def test_update_timespans(self):
        minutes = randint(10, 120)
        display = CryoSignals()
        for plot in display.plots.values():
            plot.setTimeSpan = MagicMock()

        display.update_timespans(minutes)
        for plot in display.plots.values():
            plot.setTimeSpan.assert_called_with(minutes * 60)
