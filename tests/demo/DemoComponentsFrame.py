
from logging import Logger
from logging import getLogger

from wx import Window

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedScrolledPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.MinMaxControl import MinMax
from codeallyadvanced.ui.widgets.MinMaxControl import MinMaxControl
from codeallyadvanced.ui.widgets.PositionControl import PositionControl


DEFAULT_WIDTH = 3000
A4_FACTOR:    float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20


class DemoComponentsFrame(SizedScrolledPanel):
    def __init__(self, parent: Window):

        self.logger:          Logger       = getLogger(__name__)

        super().__init__(parent=parent)

        self.maxWidth:  int  = DEFAULT_WIDTH
        self.maxHeight: int = int(self.maxWidth / A4_FACTOR)  # 1.41 is for A4 support

        nbrUnitsX: int = int(self.maxWidth / PIXELS_PER_UNIT_X)
        nbrUnitsY: int = int(self.maxHeight / PIXELS_PER_UNIT_Y)
        initPosX:  int = 0
        initPosY:  int = 0
        self.SetScrollbars(PIXELS_PER_UNIT_X, PIXELS_PER_UNIT_Y, nbrUnitsX, nbrUnitsY, initPosX, initPosY, False)

        self._valuesChanged: bool = False

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=False)

        self._layoutDemoWidgets(sizedScrolledPanel=self)

        self.Fit()
        self.SetMinSize(self.GetSize())

    def _layoutDemoWidgets(self, sizedScrolledPanel: SizedScrolledPanel):

        labelledPanel: SizedStaticBox = SizedStaticBox(sizedScrolledPanel, label='Widgets')
        labelledPanel.SetSizerProps(expand=True, proportion=1)

        horizontalPanel: SizedPanel = SizedPanel(labelledPanel)
        horizontalPanel.SetSizerType('horizontal')
        horizontalPanel.SetSizerProps(expand=True, proportion=1)

        positionControl: PositionControl = PositionControl(sizedPanel=horizontalPanel, displayText='Demo Position',
                                                           minValue=0, maxValue=2048,
                                                           valueChangedCallback=self._positionChanged,
                                                           setControlsSize=False)

        dimensionsControls: DimensionsControl = DimensionsControl(sizedPanel=horizontalPanel, displayText='Demo Dimensions',
                                                                  minValue=480, maxValue=4096,
                                                                  valueChangedCallback=self._dimensionsChanged,
                                                                  setControlsSize=False)

        minMaxX: MinMaxControl = MinMaxControl(sizedPanel=horizontalPanel, displayText='Minimum/Maximum Values',
                                               minValue=-1024, maxValue=1024,
                                               valueChangedCallback=self._onMinMaxChanged,
                                               setControlsSize=False)

        # noinspection PyUnresolvedReferences
        positionControl.SetSizerProps(expand=True, proportion=1)
        # noinspection PyUnresolvedReferences
        dimensionsControls.SetSizerProps(expand=True, proportion=1)

        positionControl.position = Position(0, 2048)
        dimensionsControls.dimensions   = Dimensions(480, 2048)
        minMaxX.minMax = MinMax(minValue=-55, maxValue=50)

    def _positionChanged(self, newPosition: Position):
        self.logger.info(f'Position changed: {newPosition=}')
        self._valuesChanged = True

    def _dimensionsChanged(self, newDimensions: Dimensions):
        self.logger.info(f'Dimensions changed: {newDimensions=}')
        self._valuesChanged = True

    def _onMinMaxChanged(self, minMaxX: MinMax):
        self.logger.info(f'MinMax changed: {minMaxX=}')
        self._valuesChanged = True

