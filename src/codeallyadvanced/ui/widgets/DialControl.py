
from logging import Logger
from logging import getLogger

from typing import Any
from typing import cast
from typing import Callable

from math import cos
from math import pi
from math import sin
from math import atan2

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

START_ANGLE_RADIANS:   float  = 0.75 * pi
SWEEP_ANGLE_RADIANS:   float  = 1.5 * pi
FULL_CIRCLE_RADIANS:   float  = 2.0 * pi
"""
Full circle angular period in radians (360 degrees, or 2 * pi).
"""
FALLBACK_ACCENT_COLOR: Colour = Colour(0, 122, 255)

EPSILON_RANGE_SPAN: float = 0.00001
"""
Minimum non-zero range span required to compute a value fraction without division-by-zero.
"""

EPSILON_STEP: float = 0.00001
"""
Minimum non-zero step increment required to snap values and prevent division-by-zero.
"""

DEFAULT_VALUE_FRACTION: float = 0.0
"""
Baseline fraction returned when the dial range is degenerate or flat.
"""

MIN_SWEEP_RENDER_FRACTION: float = 0.001
"""
Minimum progress fraction required to stroke the active sweep arc,
preventing rounded pen caps (CAP_ROUND) from bleeding onto the neutral track at zero.
"""

MIN_INNER_FACE_RADIUS: float = 8.0
"""
Minimum radius in pixels required to render the interior face disc.
Prevents cramped visual clutter and non-positive circle geometry on small dials.
"""

MIN_THUMB_RADIUS: float = 3.0
"""
Minimum radius in pixels for the rotary thumb pip.
"""

THUMB_TRACK_RATIO: float = 0.45
"""
Ratio of thumb radius to track stroke width.
"""

THUMB_SHADOW_OFFSET_Y: float = 1.0
"""
Vertical pixel offset for the thumb drop shadow.
"""

THUMB_SHADOW_SPREAD: float = 0.5
"""
Radial pixel expansion for the thumb drop shadow.
"""

THUMB_SHADOW_COLOR: Colour = Colour(0, 0, 0, 40)
"""
Translucent shadow color (alpha 40) for the thumb drop shadow.
"""

TRANSPARENT_COLOR: Colour = Colour(0, 0, 0, 0)
"""
Fully transparent color (alpha 0) for borderless pens and hollow fill brushes.
"""

FOCUS_RING_OFFSET: float = 3.0
"""
Radial pixel expansion beyond outerRadius for the accessibility focus ring.
"""

FOCUS_RING_ALPHA: int = 140
"""
Alpha opacity (0-255, ~55%) applied to the accent color for the focus ring outline.
"""

FOCUS_RING_PEN_WIDTH: int = 2
"""
Stroke width in pixels for the accessibility focus ring pen.
"""


DEFAULT_FACE_COLOR: Colour = Colour(250, 250, 252)
"""
Default background color for the inner circular face of the dial.
"""

DEFAULT_TRACK_COLOR: Colour = Colour(224, 224, 228)
"""
Default background track color for the inactive sweep arc of the dial.
"""

DEFAULT_THUMB_COLOR: Colour = Colour(255, 255, 255)
"""
Default color for the draggable knob/thumb indicator.
"""

DEFAULT_FACE_BORDER_COLOR: Colour = Colour(210, 210, 216)
"""
Default border stroke color for the inner face of the dial.
"""


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

        self.logger: Logger = getLogger(__name__)

        self._minValue: float = float(minValue)
        self._maxValue: float = float(maxValue)
        self._step:     float = float(step)
        self._value:    float = float(initialValue)
        self._valueChangedCallback: DialChangeCallback = valueChangedCallback

        self._isDragging: bool = False
        self._isHovered: bool = False

        self._faceColor:       Colour = DEFAULT_FACE_COLOR
        self._trackColor:      Colour = DEFAULT_TRACK_COLOR
        self._thumbColor:      Colour = DEFAULT_THUMB_COLOR
        self._faceBorderColor: Colour = DEFAULT_FACE_BORDER_COLOR

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
        """
        Coordinate the vector drawing of the dial control components.

        Args:
            _event: Paint event triggered by wxPython.
        """
        paintDc:         AutoBufferedPaintDC = AutoBufferedPaintDC(self)
        graphicsContext: GraphicsContext     = GraphicsContext.Create(paintDc)
        if not graphicsContext:
            self.logger.error('DialControl: Failed to create GraphicsContext from AutoBufferedPaintDC')
            return

        clientSize: Size = self.GetClientSize()
        width:      int  = clientSize.GetWidth()
        height:     int  = clientSize.GetHeight()

        centerX: float = float(width) / 2.0
        centerY: float = float(height) / 2.0
        outerRadius: float = max(10.0, min(centerX, centerY) - 8.0)
        trackWidth:  float = max(4.0, outerRadius * 0.16)

        trackRadius:     float = outerRadius - (trackWidth / 2.0)
        innerFaceRadius: float = trackRadius - (trackWidth / 2.0) - 2.0

        accentColor:   Colour = self._getAccentColor()
        valueFraction: float  = self._getValueFraction()

        self._drawTrack(graphicsContext, centerX, centerY, trackRadius, trackWidth)
        self._drawActiveSweep(graphicsContext, centerX, centerY, trackRadius, trackWidth, valueFraction, accentColor)
        self._drawFace(graphicsContext, centerX, centerY, innerFaceRadius)
        self._drawThumb(graphicsContext, centerX, centerY, trackRadius, trackWidth, valueFraction)

        if self.HasFocus():
            self._drawFocusRing(graphicsContext, centerX, centerY, outerRadius, accentColor)

    def _getAccentColor(self) -> Colour:
        """
        Retrieve system accent color or default fallback.

        Returns:
            The system highlight Colour or macOS default blue.
        """
        accentColor: Colour = SystemSettings.GetColour(SYS_COLOUR_HIGHLIGHT)
        if not accentColor.IsOk():
            accentColor = FALLBACK_ACCENT_COLOR
        return accentColor

    def _getValueFraction(self) -> float:
        """
        Calculate the normalized 0.0 to 1.0 progress fraction of the current value.

        Returns:
            Normalized float between 0.0 (minValue) and 1.0 (maxValue).
        """
        rangeSpan: float = self._maxValue - self._minValue
        if rangeSpan <= EPSILON_RANGE_SPAN:
            return DEFAULT_VALUE_FRACTION
        return (self._value - self._minValue) / rangeSpan

    def _drawTrack(
        self,
        graphicsContext: GraphicsContext,
        centerX: float,
        centerY: float,
        trackRadius: float,
        trackWidth: float
    ):
        """
        Render the circular background track arc.

        Args:
            graphicsContext: Active graphics context.
            centerX: Dial center X coordinate.
            centerY: Dial center Y coordinate.
            trackRadius: Radius of the track arc.
            trackWidth: Stroke width of the track.
        """
        trackWxPen: Pen = Pen(self._trackColor, int(trackWidth))
        trackWxPen.SetCap(CAP_ROUND)
        trackPen: GraphicsPen = graphicsContext.CreatePen(trackWxPen)

        trackPath: GraphicsPath = graphicsContext.CreatePath()
        trackPath.AddArc(
            centerX,
            centerY,
            trackRadius,
            START_ANGLE_RADIANS,
            START_ANGLE_RADIANS + SWEEP_ANGLE_RADIANS,
            True
        )
        graphicsContext.SetPen(trackPen)
        graphicsContext.StrokePath(trackPath)

    def _drawActiveSweep(
        self,
        graphicsContext: GraphicsContext,
        centerX: float,
        centerY: float,
        trackRadius: float,
        trackWidth: float,
        valueFraction: float,
        accentColor: Colour
    ):
        """
        Render the active highlight sweep arc proportional to current value.

        Args:
            graphicsContext: Active graphics context.
            centerX: Dial center X coordinate.
            centerY: Dial center Y coordinate.
            trackRadius: Radius of the track arc.
            trackWidth: Stroke width of the track.
            valueFraction: Value normalized to range [0.0, 1.0].
            accentColor: Highlight color for the sweep.
        """
        if valueFraction <= MIN_SWEEP_RENDER_FRACTION:
            return

        activeWxPen: Pen = Pen(accentColor, int(trackWidth))
        activeWxPen.SetCap(CAP_ROUND)
        activePen: GraphicsPen = graphicsContext.CreatePen(activeWxPen)

        activeSweepRadians: float = valueFraction * SWEEP_ANGLE_RADIANS
        activePath: GraphicsPath = graphicsContext.CreatePath()
        activePath.AddArc(
            centerX,
            centerY,
            trackRadius,
            START_ANGLE_RADIANS,
            START_ANGLE_RADIANS + activeSweepRadians,
            True
        )
        graphicsContext.SetPen(activePen)
        graphicsContext.StrokePath(activePath)

    def _drawFace(
        self,
        graphicsContext: GraphicsContext,
        centerX: float,
        centerY: float,
        innerFaceRadius: float
    ):
        """
        Render the interior face disc and its border.

        Args:
            graphicsContext: Active graphics context.
            centerX: Dial center X coordinate.
            centerY: Dial center Y coordinate.
            innerFaceRadius: Radius of the inner disc.
        """
        if innerFaceRadius <= MIN_INNER_FACE_RADIUS:
            return

        facePath: GraphicsPath = graphicsContext.CreatePath()
        facePath.AddCircle(centerX, centerY, innerFaceRadius)

        faceBrush: GraphicsBrush = graphicsContext.CreateBrush(Brush(self._faceColor))
        faceBorderPen: GraphicsPen = graphicsContext.CreatePen(Pen(self._faceBorderColor, 1))

        graphicsContext.SetBrush(faceBrush)
        graphicsContext.SetPen(faceBorderPen)
        graphicsContext.DrawPath(facePath)

    def _drawThumb(
        self,
        graphicsContext: GraphicsContext,
        centerX:       float,
        centerY:       float,
        trackRadius:   float,
        trackWidth:    float,
        valueFraction: float
    ):
        """
        Render the indicator thumb handle and soft drop shadow.

        Args:
            graphicsContext: Active graphics context.
            centerX: Dial center X coordinate.
            centerY: Dial center Y coordinate.
            trackRadius: Radius of the track arc.
            trackWidth: Stroke width of the track.
            valueFraction: Value normalized to range [0.0, 1.0].
        """
        currentAngleRadians: float = START_ANGLE_RADIANS + (valueFraction * SWEEP_ANGLE_RADIANS)
        thumbRadius:  float = max(MIN_THUMB_RADIUS, trackWidth * THUMB_TRACK_RATIO)
        thumbCenterX: float = centerX + (trackRadius * cos(currentAngleRadians))
        thumbCenterY: float = centerY + (trackRadius * sin(currentAngleRadians))

        thumbShadowPath: GraphicsPath = graphicsContext.CreatePath()
        thumbShadowPath.AddCircle(
            thumbCenterX,
            thumbCenterY + THUMB_SHADOW_OFFSET_Y,
            thumbRadius + THUMB_SHADOW_SPREAD
        )
        shadowBrush:    GraphicsBrush = graphicsContext.CreateBrush(Brush(THUMB_SHADOW_COLOR))
        transparentPen: GraphicsPen   = graphicsContext.CreatePen(Pen(TRANSPARENT_COLOR, 0))
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

    def _drawFocusRing(
        self,
        graphicsContext: GraphicsContext,
        centerX:     float,
        centerY:     float,
        outerRadius: float,
        accentColor: Colour
    ):
        """
        Render accessibility focus ring around the dial when focused.

        Args:
            graphicsContext: Active graphics context.
            centerX: Dial center X coordinate.
            centerY: Dial center Y coordinate.
            outerRadius: Outer boundary radius.
            accentColor: Base color for the focus outline.
        """
        focusPath: GraphicsPath = graphicsContext.CreatePath()
        focusPath.AddCircle(centerX, centerY, outerRadius + FOCUS_RING_OFFSET)

        focusColor: Colour = Colour(
            accentColor.Red(),
            accentColor.Green(),
            accentColor.Blue(),
            FOCUS_RING_ALPHA
        )

        focusPen: GraphicsPen = graphicsContext.CreatePen(Pen(focusColor, FOCUS_RING_PEN_WIDTH))
        clearBrush: GraphicsBrush = graphicsContext.CreateBrush(Brush(TRANSPARENT_COLOR))

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

        mouseAngleRadians: float = atan2(deltaY, deltaX)
        if mouseAngleRadians < 0:
            mouseAngleRadians += FULL_CIRCLE_RADIANS

        normalizedAngleRadians: float = mouseAngleRadians - START_ANGLE_RADIANS
        if normalizedAngleRadians < 0:
            normalizedAngleRadians += FULL_CIRCLE_RADIANS

        if normalizedAngleRadians <= SWEEP_ANGLE_RADIANS:
            fraction: float = normalizedAngleRadians / SWEEP_ANGLE_RADIANS
        else:
            gapDistanceMin: float = FULL_CIRCLE_RADIANS - normalizedAngleRadians
            gapDistanceMax: float = normalizedAngleRadians - SWEEP_ANGLE_RADIANS
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

        if self._step > EPSILON_STEP:
            stepCount: float = round((clamped - self._minValue) / self._step)
            snapped: float = self._minValue + (stepCount * self._step)
            return max(self._minValue, min(self._maxValue, snapped))

        return clamped
