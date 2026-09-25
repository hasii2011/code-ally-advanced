
from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Position import Position

from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerControl
from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerParameters
from codeallyadvanced.ui.widgets.DualSpinnerControl import SpinnerValues
from codeallyadvanced.ui.widgets.DualSpinnerControl import ValueChangeCallback


@dataclass
class PositionParameters(DualSpinnerParameters):
    minValue:           int = 0
    maxValue:           int = 2048
    firstSpinnerLabel:  str = 'X:'
    secondSpinnerLabel: str = 'Y:'


class PositionControl(DualSpinnerControl):
    """
    A facade around the basic dual-spinner control;   Essentially
        * Converts the spinner values to and from the Position type;
        * Handles the spinner callback
        * Forwards the spinner values as Position values

    """
    POSITION_MIN_VALUE: int = 0     # For the control only
    POSITION_MAX_VALUE: int = 2048  # For the control only

    def __init__(self, parent: SizedPanel, parameters: PositionParameters):
        """

        Args:
            parent:     The parent window
            parameters: Configuration parameters for the position control
        """
        self.logger:                   Logger              = getLogger(__name__)
        self._positionChangedCallback: ValueChangeCallback = parameters.valueChangedCallback
        self._position:                Position            = Position()

        super().__init__(parent=parent, parameters=parameters)

    def _setPosition(self, newValue: Position):
        self._position = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.x, value1=newValue.y)

    # noinspection PyPropertyDefinition
    # noinspection PyTypeChecker
    position = property(fget=None, fset=_setPosition, fdel=None, doc='Write only property to set values')

    def _notifyValueChanged(self, spinnerValues: SpinnerValues):
        self.logger.info(f'{spinnerValues}')
        self._position.x = spinnerValues.value0
        self._position.y = spinnerValues.value1

        if self._positionChangedCallback is not None:
            self._positionChangedCallback(self._position)
