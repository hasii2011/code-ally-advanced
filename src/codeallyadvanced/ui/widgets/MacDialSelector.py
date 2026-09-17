from typing import Any
from typing import Callable
from typing import cast

from dataclasses import dataclass

from logging import Logger
from logging import getLogger

from wx import ALIGN_CENTER_HORIZONTAL
from wx import ID_ANY
from wx import Size
from wx import StaticText

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.ui.widgets.DialControl import DialControl
from codeallyadvanced.ui.widgets.DialControl import DialEvent
from codeallyadvanced.ui.widgets.DialControl import EVT_DIAL_CHANGED

FormatValueCallback = Callable[[float], str]
ValueChangeCallback = Callable[[float], None]

NO_FORMAT_CALLBACK: FormatValueCallback = cast(FormatValueCallback, None)
NO_VALUE_CALLBACK: ValueChangeCallback = cast(ValueChangeCallback, None)


@dataclass
class MacDialSelectorParameters:
    """
    Configuration parameters for constructing a MacDialSelector component.

    Attributes:
        minValue: Minimum selectable value in the domain range.
        maxValue: Maximum selectable value in the domain range.
        initialValue: Starting value set when the widget initializes.
        step: Increment step value applied when turning or stepping.
        dialLabel: Text title displayed on the group box border.
        dialWidth: Preferred pixel width of the embedded DialControl.
        dialHeight: Preferred pixel height of the embedded DialControl.
        formatValueCallback: Formatter mapping numeric value to display string.
        valueChangedCallback: Listener invoked when the reported value changes.
    """
    minValue: float = 0.0
    maxValue: float = 100.0
    initialValue: float = 0.0
    step: float = 1.0
    dialLabel: str = ''
    dialWidth: int = 100
    dialHeight: int = 100
    formatValueCallback: FormatValueCallback = NO_FORMAT_CALLBACK
    valueChangedCallback: ValueChangeCallback = NO_VALUE_CALLBACK


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
        self._value: float = float(parameters.initialValue)

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        dialSize: Size = Size(parameters.dialWidth, parameters.dialHeight)
        self._dialCtrl: DialControl = DialControl(
            parent=self,
            minValue=parameters.minValue,
            maxValue=parameters.maxValue,
            initialValue=parameters.initialValue,
            step=parameters.step,
            size=dialSize
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

        if self._parameters.valueChangedCallback is not None:
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
            if value.is_integer():
                displayLabel = f'{int(value)}'
            else:
                displayLabel = f'{value:.2f}'

        self._valueTracker.SetLabel(displayLabel)
        self._valueTracker.Refresh()
