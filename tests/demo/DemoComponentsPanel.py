
from logging import Logger
from logging import getLogger


from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from codeallyadvanced.ui.widgets.DimensionsControl import DimensionsControl
from codeallyadvanced.ui.widgets.DirectorySelector import DirectorySelector
from codeallyadvanced.ui.widgets.MinMaxControl import MinMax
from codeallyadvanced.ui.widgets.MinMaxControl import MinMaxControl
from codeallyadvanced.ui.widgets.PositionControl import PositionControl


class DemoComponentsPanel(SizedPanel):
    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self._valuesChanged: bool = False

        self.SetSizerType('horizontal')

        self._layoutSpinnerWidgets(parentPanel=self)
        self._layoutDirectorySelector(parentPanel=self)

        self.Fit()
        self.SetMinSize(self.GetSize())

    def _layoutSpinnerWidgets(self, parentPanel: SizedPanel):

        labelledPanel: SizedStaticBox = SizedStaticBox(parentPanel, label='Widgets')
        labelledPanel.SetSizerProps(expand=True, proportion=1)

        demoPanel: SizedPanel = SizedPanel(labelledPanel)
        demoPanel.SetSizerType('vertical')
        demoPanel.SetSizerProps(expand=True, proportion=1)

        positionControl: PositionControl = PositionControl(sizedPanel=demoPanel, displayText='Demo Position',
                                                           minValue=0, maxValue=2048,
                                                           valueChangedCallback=self._positionChanged,
                                                           setControlsSize=False)

        dimensionsControls: DimensionsControl = DimensionsControl(sizedPanel=demoPanel, displayText='Demo Dimensions',
                                                                  minValue=480, maxValue=4096,
                                                                  valueChangedCallback=self._dimensionsChanged,
                                                                  setControlsSize=False)

        minMaxX: MinMaxControl = MinMaxControl(sizedPanel=demoPanel, displayText='Minimum/Maximum Values',
                                               minValue=-1024, maxValue=1024,
                                               valueChangedCallback=self._onMinMaxChanged,
                                               setControlsSize=False)

        positionControl.SetSizerProps(expand=True, proportion=1)
        dimensionsControls.SetSizerProps(expand=True, proportion=1)

        positionControl.position = Position(0, 2048)
        dimensionsControls.dimensions   = Dimensions(480, 2048)
        minMaxX.minMax = MinMax(minValue=-55, maxValue=50)

    def _layoutDirectorySelector(self, parentPanel: SizedPanel):

        labelledPanel: SizedStaticBox = SizedStaticBox(parentPanel, label='Directory Selector')
        labelledPanel.SetSizerProps(expand=True, proportion=2)  # I want twice as much space as the spinner containers

        directorySelector: DirectorySelector = DirectorySelector(parent=labelledPanel)

    def _positionChanged(self, newPosition: Position):
        self.logger.info(f'Position changed: {newPosition=}')
        self._valuesChanged = True

    def _dimensionsChanged(self, newDimensions: Dimensions):
        self.logger.info(f'Dimensions changed: {newDimensions=}')
        self._valuesChanged = True

    def _onMinMaxChanged(self, minMaxX: MinMax):
        self.logger.info(f'MinMax changed: {minMaxX=}')
        self._valuesChanged = True
