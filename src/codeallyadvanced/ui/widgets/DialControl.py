
from typing import Any
from typing import Callable
from typing import cast

from math import atan2
from math import cos
from math import pi
from math import sin

from wx import AutoBufferedPaintDC
from wx import Brush
from wx import CAP_ROUND
from wx import Control
from wx import EraseEvent
from wx import FocusEvent
from wx import GraphicsBrush
from wx import GraphicsContext
from wx import GraphicsPath
from wx import GraphicsPen
from wx import ID_ANY
from wx import KeyEvent
from wx import MouseEvent
from wx import NewEventType
from wx import PaintEvent
from wx import Pen
from wx import SizeEvent
from wx import Point
from wx import PyCommandEvent
from wx import PyEventBinder
from wx import Size
from wx import SystemSettings
from wx import SYS_COLOUR_HIGHLIGHT
from wx import TAB_TRAVERSAL
from wx import WANTS_CHARS
from wx import WXK_DOWN
from wx import WXK_END
from wx import WXK_HOME
from wx import WXK_LEFT
from wx import WXK_PAGEDOWN
from wx import WXK_PAGEUP
from wx import WXK_RIGHT
from wx import WXK_UP

from wx import EVT_ERASE_BACKGROUND
from wx import EVT_KEY_DOWN
from wx import EVT_KILL_FOCUS
from wx import EVT_LEFT_DOWN
from wx import EVT_LEFT_UP
from wx import EVT_MOTION
from wx import EVT_MOUSEWHEEL
from wx import EVT_PAINT
from wx import EVT_SET_FOCUS
from wx import EVT_SIZE

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from wx import Colour

wxEVT_DIAL_CHANGED: int = NewEventType()

EXPECTED_CONTROL_IDS: int = 1
"""
Single control command events (expects 1 ID or source widget when bound via EvtHandler.Bind()).
"""

EVT_DIAL_CHANGED: PyEventBinder = PyEventBinder(wxEVT_DIAL_CHANGED, EXPECTED_CONTROL_IDS)

DialChangeCallback = Callable[[float], Any]

NO_DIAL_CALLBACK: DialChangeCallback = cast(DialChangeCallback, None)


class DialEvent(PyCommandEvent):
    """
    Custom command event fired whenever the DialControl value is changed.

    Attributes:
        _value: The current floating-point value of the dial at the time of the event.
    """

    def __init__(self, eventType: int, winId: int, value: float):
        """
        Initialize the dial command event.

        Args:
            eventType: The wx event type identifier (wxEVT_DIAL_CHANGED).
            winId:     Window identifier of the control firing the event.
            value:     The new numerical value of the dial.
        """
        super().__init__(eventType, winId)
        self._value: float = value

    def GetValue(self) -> float:
        """
        Retrieve the current numerical value associated with this event.

        Returns:
            The dial's current floating-point value.
        """
        return self._value


class DialControl(Control):
    """
    A modern macOS-style rotary dial control built on wx.GraphicsContext.

    This custom control implements a smooth anti-aliased vector rendering optimized
    for Retina/HiDPI
    displays.  It adheres to macOS Human Interface Guidelines it has:
      * System accent highlight sweeps
      * Neutral background tracks
      * A sleek thumb pip with depth shading
      * A keyboard focus ring.

    User can use the follow to interact with it:
        * Circular Drag:          Click or drag radially around the dial center.
        * Trackpad / Mouse Wheel: Step values via EVT_MOUSEWHEEL.
        * Keyboard Navigation:    Arrow keys, PageUp/PageDown, and Home/End.
    """

    START_ANGLE_RAD: float = 0.75 * pi
    SWEEP_ANGLE_RAD: float = 1.5 * pi

    def __init__(self,
                 parent:       SizedPanel | SizedStaticBox,
                 winId:        int = ID_ANY,
                 minValue:     float = 0.0,
                 maxValue:     float = 100.0,
                 initialValue: float = 0.0,
                 step:         float = 1.0,
                 size:         Size = Size(100, 100),
                 valueChangedCallback: DialChangeCallback = NO_DIAL_CALLBACK):
        """
        The DialControl constructor

        Args:
            parent:               Parent sized container hosting this control (SizedPanel or SizedStaticBox).
            winId:                Window identifier. Defaults to ID_ANY.
            minValue:             Lower bound of the dial range. Defaults to 0.0.
            maxValue:             Upper bound of the dial range. Defaults to 100.0.
            initialValue:         Initial numerical position within [minValue, maxValue]. Defaults to 0.0.
            step:                 Incremental step value for snapping, wheel, and keyboard navigation. Defaults to 1.0.
            size:                 Initial dimensions of the widget. Defaults to Size(100, 100).
            valueChangedCallback: Optional direct callback invoked when the value changes. Defaults to NO_DIAL_CALLBACK.
        """
        style: int = TAB_TRAVERSAL | WANTS_CHARS
        super().__init__(parent, winId, size=size, style=style)

        self._minValue: float = float(minValue)
        self._maxValue: float = float(maxValue)
        self._step:     float = float(step)
        self._value:    float = float(initialValue)
        self._valueChangedCallback: DialChangeCallback = valueChangedCallback

        self._isDragging: bool = False
        self._isHovered: bool = False

        self._faceColor:       Colour = Colour(250, 250, 252)
        self._trackColor:      Colour = Colour(224, 224, 228)
        self._thumbColor:      Colour = Colour(255, 255, 255)
        self._faceBorderColor: Colour = Colour(210, 210, 216)

        self.SetInitialSize(size)
        self.SetBackgroundStyle(cast(Any, 2))

        self.Bind(EVT_PAINT, self._onPaint)
        self.Bind(EVT_SIZE, self._onSize)
        self.Bind(EVT_ERASE_BACKGROUND, self._onEraseBackground)
        self.Bind(EVT_LEFT_DOWN, self._onLeftDown)
        self.Bind(EVT_LEFT_UP, self._onLeftUp)
        self.Bind(EVT_MOTION, self._onMotion)
        self.Bind(EVT_MOUSEWHEEL, self._onMouseWheel)
        self.Bind(EVT_KEY_DOWN, self._onKeyDown)
        self.Bind(EVT_SET_FOCUS, self._onSetFocus)
        self.Bind(EVT_KILL_FOCUS, self._onKillFocus)

    @property
    def minValue(self) -> float:
        """
        Retrieve the lower bound of the dial.
        """
        return self._minValue

    @minValue.setter
    def minValue(self, newMinValue: float):
        """
        Set the lower bound of the dial and trigger a visual refresh.

        Args:
            newMinValue: The new minimum value.
        """
        self._minValue = float(newMinValue)
        self.Refresh()

    @property
    def maxValue(self) -> float:
        """
        Retrieve the upper bound of the dial.
        """
        return self._maxValue

    @maxValue.setter
    def maxValue(self, newMaxValue: float):
        """
        Set the upper bound of the dial and trigger a visual refresh.

        Args:
            newMaxValue: The new maximum value.
        """
        self._maxValue = float(newMaxValue)
        self.Refresh()

    @property
    def step(self) -> float:
        """
        Retrieve the incremental step size.
        """
        return self._step

    @step.setter
    def step(self, newStep: float):
        """
        Set the incremental step size.

        Args:
            newStep: The step size increment (must be > 0).
        """
        self._step = max(0.0001, float(newStep))

    @property
    def value(self) -> float:
        """
        Retrieve the current value of the dial.
        """
        return self._value

    @value.setter
    def value(self, newValue: float):
        """
        Set the value of the dial, clamping and snapping to step intervals.

        Args:
            newValue: The new value to assign.
        """
        clampedValue: float = self._clampAndSnap(float(newValue))
        if clampedValue != self._value:
            self._value = clampedValue
            self.Refresh()

    @property
    def valueChangedCallback(self) -> DialChangeCallback:
        """
        Retrieve the current value-changed callback.
        """
        return self._valueChangedCallback

    @valueChangedCallback.setter
    def valueChangedCallback(self, newCallback: DialChangeCallback):
        """
        Set the callback invoked on value updates.

        Args:
            newCallback: Callable accepting the updated float value.
        """
        self._valueChangedCallback = newCallback

    def DoGetBestSize(self) -> Size:
        """
        Provide the recommended default dimensions for the control.

        Returns:
            The default Size(100, 100).
        """
        return Size(100, 100)

    def AcceptsFocus(self) -> bool:
        """
        Indicate whether the control accepts keyboard focus traversal.

        Returns:
            True to enable Tab key traversal and keyboard interaction.
        """
        return True

    def _onPaint(self, _event: PaintEvent):
        paintDc: AutoBufferedPaintDC = AutoBufferedPaintDC(self)
        graphicsContext: GraphicsContext = GraphicsContext.Create(paintDc)
        if not graphicsContext:
            return

        clientSize: Size = self.GetClientSize()
        width: int = clientSize.GetWidth()
        height: int = clientSize.GetHeight()

        centerX: float = float(width) / 2.0
        centerY: float = float(height) / 2.0
        outerRadius: float = max(10.0, min(centerX, centerY) - 8.0)
        trackWidth: float = max(4.0, outerRadius * 0.16)
        trackRadius: float = outerRadius - (trackWidth / 2.0)
        innerFaceRadius: float = trackRadius - (trackWidth / 2.0) - 2.0

        accentColor: Colour = SystemSettings.GetColour(SYS_COLOUR_HIGHLIGHT)
        if not accentColor.IsOk():
            accentColor = Colour(0, 122, 255)

        trackWxPen: Pen = Pen(self._trackColor, int(trackWidth))
        trackWxPen.SetCap(CAP_ROUND)
        trackPen: GraphicsPen = graphicsContext.CreatePen(trackWxPen)

        activeWxPen: Pen = Pen(accentColor, int(trackWidth))
        activeWxPen.SetCap(CAP_ROUND)
        activePen: GraphicsPen = graphicsContext.CreatePen(activeWxPen)

        trackPath: GraphicsPath = graphicsContext.CreatePath()
        trackPath.AddArc(
            centerX,
            centerY,
            trackRadius,
            self.START_ANGLE_RAD,
            self.START_ANGLE_RAD + self.SWEEP_ANGLE_RAD,
            True
        )
        graphicsContext.SetPen(trackPen)
        graphicsContext.StrokePath(trackPath)

        valueFraction: float = self._getValueFraction()
        if valueFraction > 0.001:
            activeSweepRad: float = valueFraction * self.SWEEP_ANGLE_RAD
            activePath: GraphicsPath = graphicsContext.CreatePath()
            activePath.AddArc(
                centerX,
                centerY,
                trackRadius,
                self.START_ANGLE_RAD,
                self.START_ANGLE_RAD + activeSweepRad,
                True
            )
            graphicsContext.SetPen(activePen)
            graphicsContext.StrokePath(activePath)

        if innerFaceRadius > 8.0:
            facePath: GraphicsPath = graphicsContext.CreatePath()
            facePath.AddCircle(centerX, centerY, innerFaceRadius)
            faceBrush: GraphicsBrush = graphicsContext.CreateBrush(Brush(self._faceColor))
            faceBorderPen: GraphicsPen = graphicsContext.CreatePen(Pen(self._faceBorderColor, 1))
            graphicsContext.SetBrush(faceBrush)
            graphicsContext.SetPen(faceBorderPen)
            graphicsContext.DrawPath(facePath)

        currentAngleRad: float = self.START_ANGLE_RAD + (valueFraction * self.SWEEP_ANGLE_RAD)
        thumbRadius: float = max(3.0, trackWidth * 0.45)
        thumbCenterX: float = centerX + (trackRadius * cos(currentAngleRad))
        thumbCenterY: float = centerY + (trackRadius * sin(currentAngleRad))

        thumbShadowPath: GraphicsPath = graphicsContext.CreatePath()
        thumbShadowPath.AddCircle(thumbCenterX, thumbCenterY + 1.0, thumbRadius + 0.5)
        shadowBrush: GraphicsBrush = graphicsContext.CreateBrush(Brush(Colour(0, 0, 0, 40)))
        transparentPen: GraphicsPen = graphicsContext.CreatePen(Pen(Colour(0, 0, 0, 0), 0))
        graphicsContext.SetBrush(shadowBrush)
        graphicsContext.SetPen(transparentPen)
        graphicsContext.DrawPath(thumbShadowPath)

        thumbPath: GraphicsPath = graphicsContext.CreatePath()
        thumbPath.AddCircle(thumbCenterX, thumbCenterY, thumbRadius)
        thumbBrush: GraphicsBrush = graphicsContext.CreateBrush(Brush(self._thumbColor))
        thumbBorderPen: GraphicsPen = graphicsContext.CreatePen(Pen(self._faceBorderColor, 1))
        graphicsContext.SetBrush(thumbBrush)
        graphicsContext.SetPen(thumbBorderPen)
        graphicsContext.DrawPath(thumbPath)

        if self.HasFocus():
            focusPath: GraphicsPath = graphicsContext.CreatePath()
            focusPath.AddCircle(centerX, centerY, outerRadius + 3.0)
            focusColor: Colour = Colour(accentColor.Red(), accentColor.Green(), accentColor.Blue(), 140)
            focusPen: GraphicsPen = graphicsContext.CreatePen(Pen(focusColor, 2))
            clearBrush: GraphicsBrush = graphicsContext.CreateBrush(Brush(Colour(0, 0, 0, 0)))
            graphicsContext.SetPen(focusPen)
            graphicsContext.SetBrush(clearBrush)
            graphicsContext.StrokePath(focusPath)

    def _onSize(self, event: SizeEvent):
        self.Refresh()
        event.Skip()

    def _onEraseBackground(self, event: EraseEvent):
        """
        Prevent background flickering during redraws.
        """
        pass

    def _onLeftDown(self, event: MouseEvent):
        self.SetFocus()
        if not self.HasCapture():
            self.CaptureMouse()
        self._isDragging = True
        self._updateValueFromMouse(event.GetPosition())

    def _onLeftUp(self, _event: MouseEvent):

        if self.HasCapture():
            self.ReleaseMouse()
        self._isDragging = False

    def _onMotion(self, event: MouseEvent):
        if self._isDragging and event.Dragging() and event.LeftIsDown():
            self._updateValueFromMouse(event.GetPosition())

    def _onMouseWheel(self, event: MouseEvent):
        wheelRotation: int = event.GetWheelRotation()
        directionStep: float = self._step if wheelRotation > 0 else -self._step
        self._setValueAndNotify(self._value + directionStep)

    def _onKeyDown(self, event: KeyEvent):
        keyCode: int = event.GetKeyCode()
        if keyCode in (WXK_LEFT, WXK_DOWN):
            self._setValueAndNotify(self._value - self._step)
        elif keyCode in (WXK_RIGHT, WXK_UP):
            self._setValueAndNotify(self._value + self._step)
        elif keyCode == WXK_PAGEUP:
            self._setValueAndNotify(self._value + (self._step * 10.0))
        elif keyCode == WXK_PAGEDOWN:
            self._setValueAndNotify(self._value - (self._step * 10.0))
        elif keyCode == WXK_HOME:
            self._setValueAndNotify(self._minValue)
        elif keyCode == WXK_END:
            self._setValueAndNotify(self._maxValue)
        else:
            event.Skip()

    def _onSetFocus(self, event: FocusEvent):
        self.Refresh()
        event.Skip()

    def _onKillFocus(self, event: FocusEvent):
        self.Refresh()
        event.Skip()

    def _updateValueFromMouse(self, mousePos: Point):
        """
        Compute the angular position from mouse coordinates and map it to dial range.

        Args:
            mousePos: The current client coordinates of the mouse cursor.
        """
        clientSize: Size = self.GetClientSize()
        centerX: float = float(clientSize.GetWidth()) / 2.0
        centerY: float = float(clientSize.GetHeight()) / 2.0

        deltaX: float = float(mousePos.x) - centerX
        deltaY: float = float(mousePos.y) - centerY

        mouseAngleRad: float = atan2(deltaY, deltaX)
        if mouseAngleRad < 0:
            mouseAngleRad += 2.0 * pi

        normalizedAngleRad: float = mouseAngleRad - self.START_ANGLE_RAD
        if normalizedAngleRad < 0:
            normalizedAngleRad += 2.0 * pi

        if normalizedAngleRad <= self.SWEEP_ANGLE_RAD:
            fraction: float = normalizedAngleRad / self.SWEEP_ANGLE_RAD
        else:
            gapDistanceMin: float = (2.0 * pi) - normalizedAngleRad
            gapDistanceMax: float = normalizedAngleRad - self.SWEEP_ANGLE_RAD
            fraction = 0.0 if gapDistanceMin < gapDistanceMax else 1.0

        targetValue: float = self._minValue + (fraction * (self._maxValue - self._minValue))
        self._setValueAndNotify(targetValue)

    def _setValueAndNotify(self, rawValue: float):
        """
        Clamp and snap the proposed value, refresh the canvas, and dispatch notifications.

        Dispatches EVT_DIAL_CHANGED and triggers valueChangedCallback if configured.

        Args:
            rawValue: Unconstrained target value to apply.
        """
        clampedValue: float = self._clampAndSnap(rawValue)
        if clampedValue != self._value:
            self._value = clampedValue
            self.Refresh()

            if self._valueChangedCallback is not None:
                self._valueChangedCallback(self._value)

            dialEvent: DialEvent = DialEvent(wxEVT_DIAL_CHANGED, self.GetId(), self._value)
            dialEvent.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(dialEvent)

    def _clampAndSnap(self, valueToClamp: float) -> float:
        """
        Constrain a numerical value within [minValue, maxValue] and snap to step multiples.

        Args:
            valueToClamp: Raw numerical value.

        Returns:
            Clamped and step-aligned floating-point value.
        """
        clamped: float = max(self._minValue, min(self._maxValue, valueToClamp))
        if self._step > 0.00001:
            stepCount: float = round((clamped - self._minValue) / self._step)
            snapped: float = self._minValue + (stepCount * self._step)
            return max(self._minValue, min(self._maxValue, snapped))
        return clamped

    def _getValueFraction(self) -> float:
        """
        Calculate the normalized 0.0 to 1.0 progress fraction of the current value.

        Returns:
            Normalized float between 0.0 (minValue) and 1.0 (maxValue).
        """
        rangeSpan: float = self._maxValue - self._minValue
        if rangeSpan <= 0.00001:
            return 0.0
        return (self._value - self._minValue) / rangeSpan
