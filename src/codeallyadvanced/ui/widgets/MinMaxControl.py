
from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx.lib.sized_controls import SizedPanel

from codeallybasic.MinMax import MinMax

from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerControl
from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerParameters
from codeallyadvanced.ui.widgets.DualSpinnerControl import SpinnerValues
from codeallyadvanced.ui.widgets.DualSpinnerControl import ValueChangeCallback


@dataclass
class MinMaxParameters(DualSpinnerParameters):
    minValue:           int = -1024
    maxValue:           int = 1024
    firstSpinnerLabel:  str = 'Min:'
    secondSpinnerLabel: str = 'Max:'


class MinMaxControl(DualSpinnerControl):
    """
    A facade around the basic dual spinner control for MinMax values.
    """
    def __init__(self, parent: SizedPanel, parameters: MinMaxParameters):
        """

        Args:
            parent:     The parent window
            parameters: Configuration parameters for the min/max control
        """
        self.logger:                 Logger              = getLogger(__name__)
        self._valuesChangedCallback: ValueChangeCallback = parameters.valueChangedCallback
        self._minMax:                MinMax              = MinMax()

        super().__init__(parent=parent, parameters=parameters)

    def _setMinMax(self, newValue: MinMax):
        self._minMax = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.minValue, value1=newValue.maxValue)

    # noinspection PyPropertyDefinition
    # noinspection PyTypeChecker
    minMax = property(fget=None, fset=_setMinMax, fdel=None, doc='Write only property to set values')

    def _notifyValueChanged(self, spinnerValues: SpinnerValues):

        self.logger.info(f'{spinnerValues}')
        self._minMax.minValue = spinnerValues.value0
        self._minMax.maxValue = spinnerValues.value1

        if self._valuesChangedCallback is not None:
            self._valuesChangedCallback(self._minMax)
