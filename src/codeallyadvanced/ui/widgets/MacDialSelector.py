
from typing import Callable

from logging import Logger
from logging import getLogger

from dataclasses import dataclass
from dataclasses import field

from wx import ID_ANY
from wx import ALIGN_CENTER_HORIZONTAL

from wx import Size
from wx import StaticText

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DialControl import EVT_DIAL_CHANGED

from codeallyadvanced.ui.widgets.DialControl import DialEvent
from codeallyadvanced.ui.widgets.DialControl import DialControl

FormatValueCallback = Callable[[float], str] | None
ValueChangeCallback = Callable[[float], None]

NO_FORMAT_CALLBACK: FormatValueCallback = None

DEFAULT_MIN_VALUE: float = 0.0
"""
Default minimum selectable value for the dial domain range.
"""

DEFAULT_MAX_VALUE: float = 100.0
"""
Default maximum selectable value for the dial domain range.
"""

DEFAULT_INITIAL_VALUE: float = 0.0
"""
Default initial starting value for the dial.
"""

DEFAULT_STEP: float = 1.0
"""
Default increment step value applied when turning or stepping the dial.
"""

DEFAULT_DIAL_LABEL: str = ''
"""
Default text title displayed on the group box border.
"""

DEFAULT_DIAL_WIDTH: int = 100
"""
Default preferred pixel width of the embedded rotary dial.
"""

DEFAULT_DIAL_HEIGHT: int = 100
"""
Default preferred pixel height of the embedded rotary dial.
"""

DEFAULT_DIAL_SIZE: Size = Size(DEFAULT_DIAL_WIDTH, DEFAULT_DIAL_HEIGHT)
"""
Default preferred pixel dimensions of the embedded rotary dial.
"""


@dataclass
class ValueRange:
    """
    Mathematical domain bounds and step resolution for numeric controls.

    Attributes:
        minValue:     Minimum selectable value in the domain range. Defaults to DEFAULT_MIN_VALUE (0.0).
        maxValue:     Maximum selectable value in the domain range. Defaults to DEFAULT_MAX_VALUE (100.0).
        initialValue: Starting value set when the widget initializes. Defaults to DEFAULT_INITIAL_VALUE (0.0).
        step:         Increment step value applied when turning or stepping. Defaults to DEFAULT_STEP (1.0).
    """
    minValue:     float = DEFAULT_MIN_VALUE
    maxValue:     float = DEFAULT_MAX_VALUE
    initialValue: float = DEFAULT_INITIAL_VALUE
    step:         float = DEFAULT_STEP


@dataclass
class MacDialSelectorParameters:
    """
    Configuration parameters for constructing a MacDialSelector component.

    Attributes:
        valueChangedCallback: Mandatory listener invoked when the reported value changes.
        valueRange:           Mathematical domain bounds and step resolution. Defaults to ValueRange().
        dialLabel:            Text title displayed on the group box border. Defaults to DEFAULT_DIAL_LABEL ('').
        dialSize:             Preferred pixel dimensions of the embedded rotary dial. Defaults to DEFAULT_DIAL_SIZE (Size(100, 100)).
        formatValueCallback:  Optional formatter mapping numeric value to display string. Defaults to NO_FORMAT_CALLBACK (None).
    """
    valueChangedCallback: ValueChangeCallback
    valueRange:           ValueRange = field(default_factory=ValueRange)
    dialLabel:            str        = DEFAULT_DIAL_LABEL
    dialSize:             Size       = field(default_factory=lambda: Size(DEFAULT_DIAL_WIDTH, DEFAULT_DIAL_HEIGHT))
    formatValueCallback:  FormatValueCallback = NO_FORMAT_CALLBACK


class MacDialSelector(SizedStaticBox):
    """
    A macOS-styled rotary dial selector composite component.

    Wraps the vector-rendered DialControl inside a titled SizedStaticBox
    and couples it with a centered StaticText readout label that automatically
    updates in real time via formatValueCallback.
    """

    def __init__(self, parent: SizedPanel | SizedStaticBox, parameters: MacDialSelectorParameters):
        """
        Initialize the MacDialSelector.

        Args:
            parent: Parent sized container hosting this component (SizedPanel or SizedStaticBox).
            parameters: Configuration parameters dataclass defining bounds, step, label, and callbacks.
        """
        super().__init__(parent, label=parameters.dialLabel)
        self.logger: Logger = getLogger(__name__)

        self._parameters: MacDialSelectorParameters = parameters
        self._value:      float                     = float(parameters.valueRange.initialValue)

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self._dialCtrl: DialControl = DialControl(
            parent=self,
            minValue=parameters.valueRange.minValue,
            maxValue=parameters.valueRange.maxValue,
            initialValue=parameters.valueRange.initialValue,
            step=parameters.valueRange.step,
            size=parameters.dialSize
        )
        self._dialCtrl.SetSizerProps(expand=False, proportion=0, halign='center')

        self._valueTracker: StaticText = StaticText(
            parent=self,
            id=ID_ANY,
            label='',
            style=ALIGN_CENTER_HORIZONTAL
        )
        self._valueTracker.SetSizerProps(expand=True, proportion=0)

        self._displayValue(value=self._value)

        self.Bind(EVT_DIAL_CHANGED, self._onDialChanged, self._dialCtrl)

    @property
    def value(self) -> float:
        """
        Retrieve the current domain value.
        """
        return self._value

    @value.setter
    def value(self, newValue: float):
        """
        Assign a new value, update the dial knob, and refresh the readout label.

        Args:
            newValue: The new numeric value.
        """
        self._value = float(newValue)
        self._dialCtrl.value = self._value
        self._displayValue(value=self._value)

    @property
    def minValue(self) -> float:
        """
        Retrieve the minimum allowable domain value.
        """
        return self._dialCtrl.minValue

    @minValue.setter
    def minValue(self, newMinValue: float):
        """
        Update the minimum allowable domain value.

        Args:
            newMinValue: Lower bound value.
        """
        self._dialCtrl.minValue = float(newMinValue)
        self._displayValue(value=self._value)

    @property
    def maxValue(self) -> float:
        """
        Retrieve the maximum allowable domain value.
        """
        return self._dialCtrl.maxValue

    @maxValue.setter
    def maxValue(self, newMaxValue: float):
        """
        Update the maximum allowable domain value.

        Args:
            newMaxValue: Upper bound value.
        """
        self._dialCtrl.maxValue = float(newMaxValue)
        self._displayValue(value=self._value)

    @property
    def step(self) -> float:
        """
        Retrieve the stepping increment.
        """
        return self._dialCtrl.step

    @step.setter
    def step(self, newStep: float):
        """
        Update the stepping increment.

        Args:
            newStep: The step size increment.
        """
        self._dialCtrl.step = float(newStep)

    def _onDialChanged(self, event: DialEvent):
        """
        Handle EVT_DIAL_CHANGED from the embedded DialControl, updating the label and notifying callers.

        Args:
            event: The dial change event carrying the latest value.
        """
        reportedValue: float = event.GetValue()
        self._value = reportedValue
        self._displayValue(value=reportedValue)

        self._parameters.valueChangedCallback(self._value)

        event.Skip()

    def _displayValue(self, value: float):
        """
        Format the given value using formatValueCallback and update the tracker label.

        Args:
            value: The numeric value to render in the readout label.
        """
        displayLabel: str
        if self._parameters.formatValueCallback is not None:
            displayLabel = self._parameters.formatValueCallback(value)
        else:
            displayLabel = f'{int(value)}' if value.is_integer() else f'{value:.2f}'

        self._valueTracker.SetLabel(displayLabel)
        self._valueTracker.Refresh()
