from typing import cast

from logging import Logger
from logging import getLogger

from wx import ALIGN_CENTER_HORIZONTAL
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_ANY
from wx import ID_EXIT

from wx import App
from wx import Menu
from wx import MenuBar
from wx import Size
from wx import StaticText

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallybasic.UnitTestBase import UnitTestBase

from codeallyadvanced.ui.widgets.DialControl import DialControl
from codeallyadvanced.ui.widgets.DialControl import DialEvent
from codeallyadvanced.ui.widgets.DialControl import EVT_DIAL_CHANGED
from codeallyadvanced.ui.widgets.MacDialSelector import MacDialSelector
from codeallyadvanced.ui.widgets.MacDialSelector import MacDialSelectorParameters

FRAME_WIDTH: int = 520
FRAME_HEIGHT: int = 420


class DemoDialSelector(App):
    """
    Demonstration application showcasing the modern macOS DialControl
    alongside the DialSelector adapter.
    """

    def __init__(self, redirect: bool):
        self.logger: Logger = getLogger(__name__)
        self._appFrame: SizedFrame = cast(SizedFrame, None)
        self._directDialLabel: StaticText = cast(StaticText, None)
        self._adaptedDialLabel: StaticText = cast(StaticText, None)
        super().__init__(redirect)

    def OnInit(self):
        frameStyle: int = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        self._appFrame = SizedFrame(
            parent=None,
            title='macOS Dial Selector Demo',
            size=Size(FRAME_WIDTH, FRAME_HEIGHT),
            style=frameStyle
        )
        self._appFrame.CreateStatusBar()

        mainPane: SizedPanel = self._appFrame.GetContentsPane()
        mainPane.SetSizerType('horizontal')
        mainPane.SetSizerProps(expand=True, proportion=1)

        self._createDirectDialSection(parentPanel=mainPane)
        self._createMacDialSection(parentPanel=mainPane)
        self._createApplicationMenuBar()

        self.SetTopWindow(self._appFrame)
        self._appFrame.Show(True)

        return True

    def _createDirectDialSection(self, parentPanel: SizedPanel):
        boxContainer: SizedStaticBox = SizedStaticBox(parentPanel, label='Direct DialControl')
        boxContainer.SetSizerType('vertical')
        boxContainer.SetSizerProps(expand=True, proportion=1)

        directDial: DialControl = DialControl(
            parent=boxContainer,
            minValue=0.0,
            maxValue=100.0,
            initialValue=25.0,
            step=1.0,
            size=Size(130, 130)
        )
        directDial.SetSizerProps(expand=False, proportion=0, halign='center')

        self._directDialLabel = StaticText(
            parent=boxContainer,
            id=ID_ANY,
            label='Value: 25.0',
            style=ALIGN_CENTER_HORIZONTAL
        )
        self._directDialLabel.SetSizerProps(expand=True, proportion=0)

        helpText: StaticText = StaticText(
            parent=boxContainer,
            id=ID_ANY,
            label='Use mouse drag, wheel,\nor Arrow / PageUp / Home keys',
            style=ALIGN_CENTER_HORIZONTAL
        )
        helpText.SetSizerProps(expand=True, proportion=0)

        directDial.Bind(EVT_DIAL_CHANGED, self._onDirectDialChanged)

    def _createMacDialSection(self, parentPanel: SizedPanel):
        boxContainer: SizedStaticBox = SizedStaticBox(parentPanel, label='MacDialSelector Component')
        boxContainer.SetSizerType('vertical')
        boxContainer.SetSizerProps(expand=True, proportion=1)

        selectorParams: MacDialSelectorParameters = MacDialSelectorParameters(
            minValue=100.0,
            maxValue=1000.0,
            initialValue=440.0,
            step=10.0,
            dialLabel='Frequency (Hz)',
            formatValueCallback=self._formatAdaptedValue,
            valueChangedCallback=self._onAdaptedValueChanged
        )

        macDialSelector: MacDialSelector = MacDialSelector(parent=boxContainer, parameters=selectorParams)
        macDialSelector.SetSizerProps(expand=True, proportion=1)

        self._adaptedDialLabel = StaticText(
            parent=boxContainer,
            id=ID_ANY,
            label='Reported Value: 440 Hz',
            style=ALIGN_CENTER_HORIZONTAL
        )
        self._adaptedDialLabel.SetSizerProps(expand=True, proportion=0)

    def _onDirectDialChanged(self, event: DialEvent):
        val: float = event.GetValue()
        self._directDialLabel.SetLabel(f'Value: {val:.1f}')
        self.logger.info(f'Direct DialControl changed: {val:.1f}')
        event.Skip()

    def _onAdaptedValueChanged(self, value: float):
        if self._adaptedDialLabel:
            self._adaptedDialLabel.SetLabel(f'Reported Value: {value:.0f} Hz')
        self.logger.info(f'MacDialSelector changed: {value:.1f}')

    def _formatAdaptedValue(self, value: float) -> str:
        return f'{value:.0f} Hz'

    def _createApplicationMenuBar(self):
        menuBar: MenuBar = MenuBar()
        fileMenu: Menu = Menu()
        fileMenu.Append(ID_EXIT, '&Quit\tCtrl+Q', 'Quit Application')
        menuBar.Append(fileMenu, '&File')
        self._appFrame.SetMenuBar(menuBar)


if __name__ == '__main__':
    UnitTestBase.setUpLogging()
    demoApp: DemoDialSelector = DemoDialSelector(redirect=False)
    demoApp.MainLoop()
