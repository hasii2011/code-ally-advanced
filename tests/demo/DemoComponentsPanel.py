
from logging import Logger
from logging import getLogger

from pathlib import Path

from wx import MessageDialog
from wx import OK

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from codeallyadvanced.ui.widgets.DialSelector import DialSelector
from codeallyadvanced.ui.widgets.DialSelector import DialSelectorParameters
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

        self.SetSizerType('vertical')

        self._layoutSpinnerWidgets(parentPanel=self)
        self._layoutDirectorySelector(parentPanel=self)
        self._layoutDialSelector(parentPanel=self)

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
                                                           setControlsSize=True)

        dimensionsControls: DimensionsControl = DimensionsControl(sizedPanel=demoPanel, displayText='Demo Dimensions',
                                                                  minValue=480, maxValue=4096,
                                                                  valueChangedCallback=self._dimensionsChanged,
                                                                  setControlsSize=True)

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

        verticalPanel: SizedPanel = SizedPanel(parentPanel)
        verticalPanel.SetSizerType('vertical')
        verticalPanel.SetSizerProps(expand=True, proportion=1)

        panelNoCallback: SizedStaticBox = SizedStaticBox(verticalPanel, label='Directory Selector')
        panelNoCallback.SetSizerProps(expand=True, proportion=1)  # I want twice as much space as the spinner containers

        DirectorySelector(parent=panelNoCallback)

        panelWithCallback: SizedStaticBox = SizedStaticBox(verticalPanel, label='Directory Selector w/Callback')
        panelWithCallback.SetSizerProps(expand=True, proportion=1)  # I want twice as much space as the spinner containers

        DirectorySelector(parent=panelWithCallback, pathChangedCallback=self._pathChangedCallback)

    def _layoutDialSelector(self, parentPanel: SizedPanel):

        ds: DialSelectorParameters = DialSelectorParameters(minValue=100,
                                                            maxValue=1000,
                                                            dialLabel='Demo Dial Selector',
                                                            formatValueCallback=self._dsFormatValue,
                                                            valueChangedCallback=self._dsValueChanged,
                                                            )

        dsPanel: SizedStaticBox = SizedStaticBox(parentPanel, label='')
        dsPanel.SetSizerProps(expand=True, proportion=1)

        dialSelector: DialSelector = DialSelector(parent=dsPanel, parameters=ds)
        dialSelector.SetSizerProps(expand=True, proportion=1)

        dialSelector.tickFrequency = 50
        dialSelector.tickValue     = 20
        dialSelector.value         = 100

    def _positionChanged(self, newPosition: Position):
        self.logger.info(f'Position changed: {newPosition=}')
        self._valuesChanged = True

    def _dimensionsChanged(self, newDimensions: Dimensions):
        self.logger.info(f'Dimensions changed: {newDimensions=}')
        self._valuesChanged = True

    def _onMinMaxChanged(self, minMaxX: MinMax):
        self.logger.info(f'MinMax changed: {minMaxX=}')
        self._valuesChanged = True

    def _pathChangedCallback(self, newPath: Path):

        dlg: MessageDialog = MessageDialog(parent=None, message=f"New path: {newPath}", caption='Change', style=OK)
        dlg.ShowModal()

    def _dsFormatValue(self, valueToFormat: str):
        return f'{valueToFormat}'

    def _dsValueChanged(self, value):
        self.logger.warning(f'Dial selector changed: {value}')
