
from typing import Callable
from typing import List

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerControl
from codeallyadvanced.ui.widgets.DualSpinnerControl import SpinnerValues


@dataclass
class MinMax:
    minValue: int = 0
    maxValue: int = 0

    @classmethod
    def deSerialize(cls, value: str) -> 'MinMax':

        minMax: MinMax = MinMax()

        values: List[str] = value.split(sep=',')

        assert len(values) == 2, 'Incorrectly formatted min/max values'

        try:
            minMax.minValue = int(values[0])
            minMax.maxValue = int(values[1])
        except ValueError as ve:
            print(f'MinMax - {ve}.')
            minMax.minValue = 0
            minMax.maxValue = 0

        return minMax

    def __str__(self):
        return f'{self.minValue},{self.maxValue}'

    def __repr__(self):
        return self.__str__()


class MinMaxControl(DualSpinnerControl):
    def __init__(self, sizedPanel: SizedPanel, displayText: str,
                 valueChangedCallback: Callable,
                 minValue: int, maxValue: int,
                 setControlsSize: bool = True):

        self.logger: Logger = getLogger(__name__)

        self._valuesChangedCallback: Callable = valueChangedCallback
        self._minMax:                MinMax   = MinMax()

        super().__init__(sizedPanel, displayText, self._onSpinValueChangedCallback, minValue, maxValue, setControlsSize)

    def _setMinMax(self, newValue: MinMax):
        self._position = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.minValue, value1=newValue.maxValue)

    # noinspection PyTypeChecker
    minMax = property(fdel=None, fget=None, fset=_setMinMax, doc='Write only property to set values')

    def _onSpinValueChangedCallback(self, spinnerValues: SpinnerValues):

        self.logger.info(f'{spinnerValues}')
        self._minMax.minValue = spinnerValues.value0
        self._minMax.maxValue = spinnerValues.value1

        self._valuesChangedCallback(self._minMax)
