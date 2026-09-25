
from typing import Any
from typing import Callable
from typing import cast
from typing import Optional

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import Size
from wx import ID_ANY
from wx import EVT_TEXT
from wx import EVT_SPINCTRL
from wx import BORDER_THEME

from wx import SpinCtrl
from wx import StaticText
from wx import CommandEvent

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

SPINNER_WIDTH:          int = 80
SPINNER_HEIGHT:         int = -1    # In wxWidgets, passing -1 for height uses native platform control height
DEFAULT_CONTROL_HEIGHT: int = 58

ValueChangeCallback = Callable[[Any], None]
NO_VALUE_CALLBACK: ValueChangeCallback = cast(ValueChangeCallback, None)


@dataclass
class DualSpinnerParameters:
    caption:              str                 = ''
    valueChangedCallback: ValueChangeCallback = NO_VALUE_CALLBACK
    minValue:             int                 = 100
    maxValue:             int                 = 300
    firstSpinnerLabel:    str                 = ''
    secondSpinnerLabel:   str                 = ''
    proportion:           int                 = 0
    expand:               bool                = True


@dataclass
class SpinnerValues:
    value0: int = 0
    value1: int = 0


class DualSpinnerControl(SizedStaticBox):
    """
    A component that pairs two spinners in a horizontal panel;  Callers set
    the title to display and optionally the minimum and maximum spinner values
    Ideal for subclassing to use as a way to get x,y coordinates or width, height
    sizes
    """

    DEFAULT_MIN_VALUE: int = 100
    DEFAULT_MAX_VALUE: int = 300

    dscLogger: Logger = getLogger(__name__)     # Used as base class; So needs unique logger

    def __init__(self, parent: SizedPanel, parameters: DualSpinnerParameters):
        """

        Args:
            parent:     The parent panel
            parameters: Configuration parameters for the dual spinner control
        """

        super().__init__(parent, ID_ANY, parameters.caption, style=BORDER_THEME)

        self.SetSizerType('horizontal')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=parameters.expand, proportion=parameters.proportion)

        self._callback: ValueChangeCallback = parameters.valueChangedCallback

        self._wxSpinner0Id: int = wxNewIdRef()
        self._wxSpinner1Id: int = wxNewIdRef()

        self._firstSpinnerLabel:  Optional[StaticText] = None
        self._secondSpinnerLabel: Optional[StaticText] = None

        self._spinner0: SpinCtrl = cast(SpinCtrl, None)
        self._spinner1: SpinCtrl = cast(SpinCtrl, None)

        self._createControls(parameters)
        self._bindEventHandlers()

        self.SetMinSize(Size(-1, DEFAULT_CONTROL_HEIGHT))
        self.SetMaxSize(Size(-1, DEFAULT_CONTROL_HEIGHT))

    def _createControls(self, parameters: DualSpinnerParameters):
        """
        Instantiate labels, spin controls, and configure ranges and initial values

        Args:
            parameters: Configuration parameters for the dual spinner control
        """
        if len(parameters.firstSpinnerLabel) > 0:
            self._firstSpinnerLabel = StaticText(self, ID_ANY, parameters.firstSpinnerLabel)
            self._firstSpinnerLabel.SetSizerProps(valign='centre', border=(('right',), 5))

        self._spinner0 = SpinCtrl(self, self._wxSpinner0Id, '', size=Size(SPINNER_WIDTH, SPINNER_HEIGHT))
        self._spinner0.SetSizerProps(valign='centre', border=(('right',), 10))

        if len(parameters.secondSpinnerLabel) > 0:
            self._secondSpinnerLabel = StaticText(self, ID_ANY, parameters.secondSpinnerLabel)
            self._secondSpinnerLabel.SetSizerProps(valign='centre', border=(('right',), 5))

        self._spinner1 = SpinCtrl(self, self._wxSpinner1Id, '', size=Size(SPINNER_WIDTH, SPINNER_HEIGHT))
        self._spinner1.SetSizerProps(valign='centre')

        self._spinner0.SetRange(parameters.minValue, parameters.maxValue)
        self._spinner1.SetRange(parameters.minValue, parameters.maxValue)

        self._spinnerValues: SpinnerValues = SpinnerValues(parameters.minValue, parameters.maxValue)

    def _bindEventHandlers(self):
        """
        Bind to both text and spin events for typing and arrow clicks

        """
        self.Bind(EVT_TEXT,     self._onSpinnerValueChanged, self._spinner0)
        self.Bind(EVT_TEXT,     self._onSpinnerValueChanged, self._spinner1)
        self.Bind(EVT_SPINCTRL, self._onSpinnerValueChanged, self._spinner0)
        self.Bind(EVT_SPINCTRL, self._onSpinnerValueChanged, self._spinner1)

    def DoGetBestSize(self) -> Size:
        """
        Calculate the best size for this static box container, keeping
        a compact vertical height suitable for spinner controls.
        """
        sizerBest:  Size            = self.GetSizer().GetMinSize()
        borders:    tuple[int, int] = self.GetBordersForSizer()
        totalWidth: int             = sizerBest.width + (borders[1] * 2) + 10

        return Size(totalWidth, DEFAULT_CONTROL_HEIGHT)

    def _setSpinnerValues(self, spinnerValues: SpinnerValues):
        """
        Write only;  The appropriate way to retrieve the values is via the change callback
        Args:
            spinnerValues:
        """
        self._spinnerValues = spinnerValues
        self._spinner0.SetValue(spinnerValues.value0)
        self._spinner1.SetValue(spinnerValues.value1)
        self.dscLogger.info(f'range: {self._spinner0.GetRange()} - {self._spinner0.GetValue()=} {self._spinner1.GetValue()=}')

    # noinspection PyPropertyDefinition
    # noinspection PyTypeChecker
    spinnerValues = property(fget=None, fset=_setSpinnerValues, fdel=None, doc='Write only property to initialize spinner values')

    def enableControls(self, value: bool):
        """
        Enable or disable the spinner controls

        Args:
            value: `True` to enable, else `False`
        """
        if value is True:
            self._spinner0.Enable()
            self._spinner1.Enable()
            if self._firstSpinnerLabel is not None:
                self._firstSpinnerLabel.Enable()
            if self._secondSpinnerLabel is not None:
                self._secondSpinnerLabel.Enable()
        else:
            self._spinner0.Disable()
            self._spinner1.Disable()
            if self._firstSpinnerLabel is not None:
                self._firstSpinnerLabel.Disable()
            if self._secondSpinnerLabel is not None:
                self._secondSpinnerLabel.Disable()

    def _onSpinnerValueChanged(self, event: CommandEvent):

        eventId:  int = event.GetId()

        if eventId == self._wxSpinner0Id:
            self._spinnerValues.value0 = self._spinner0.GetValue()
        elif eventId == self._wxSpinner1Id:
            self._spinnerValues.value1 = self._spinner1.GetValue()
        else:
            self.dscLogger.error(f'Unknown spinner event id: {eventId}')

        self._notifyValueChanged(self._spinnerValues)

    def _notifyValueChanged(self, spinnerValues: SpinnerValues):
        if self._callback is not None:
            self._callback(spinnerValues)
