
from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx.lib.sized_controls import SizedPanel

from codeallybasic.Dimensions import Dimensions

from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerControl
from codeallyadvanced.ui.widgets.DualSpinnerControl import DualSpinnerParameters
from codeallyadvanced.ui.widgets.DualSpinnerControl import SpinnerValues
from codeallyadvanced.ui.widgets.DualSpinnerControl import ValueChangeCallback


@dataclass
class DimensionsParameters(DualSpinnerParameters):
    minValue:           int = 50
    maxValue:           int = 300
    firstSpinnerLabel:  str = 'W:'
    secondSpinnerLabel: str = 'H:'


class DimensionsControl(DualSpinnerControl):
    """
    A facade around the basic dual spinner control;   Essentially
        * Converts the spinner values to and from the Dimension type;
        * Handles the spinner callback
        * Forwards the spinner values as Dimension values
    """
    DIMENSION_MIN_VALUE: int = 50
    DIMENSION_MAX_VALUE: int = 300

    def __init__(self, parent: SizedPanel, parameters: DimensionsParameters):
        """

        Args:
            parent:     The parent window
            parameters: Configuration parameters for the dimensions control
        """
        self.logger:                     Logger              = getLogger(__name__)
        self._dimensionsChangedCallback: ValueChangeCallback = parameters.valueChangedCallback
        self._dimensions:                Dimensions          = Dimensions()

        super().__init__(parent=parent, parameters=parameters)

    def _setDimensions(self, newValue: Dimensions):
        self._dimensions  = newValue
        self.spinnerValues = SpinnerValues(value0=newValue.width, value1=newValue.height)

    # noinspection PyPropertyDefinition
    # noinspection PyTypeChecker
    dimensions = property(fget=None, fset=_setDimensions, fdel=None, doc='Write only property to set dimensions on control')

    def _notifyValueChanged(self, spinnerValues: SpinnerValues):
        self.logger.info(f'{spinnerValues}')

        self._dimensions.width  = spinnerValues.value0
        self._dimensions.height = spinnerValues.value1

        if self._dimensionsChangedCallback is not None:
            self._dimensionsChangedCallback(self._dimensions)
