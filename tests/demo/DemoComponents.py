
from typing import cast

from logging import Logger
from logging import getLogger

from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import ID_EXIT

from wx import App
from wx import Menu
from wx import MenuBar

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from tests.demo.DemoComponentsPanel import DemoComponentsPanel


FRAME_WIDTH:  int = 575
FRAME_HEIGHT: int = 300

JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfig.json"
TEST_DIRECTORY:               str = 'tests'

RESOURCES_PACKAGE_NAME: str = 'tests.resources'


class DemoComponents(App):

    def __init__(self, redirect: bool):

        self.logger: Logger = getLogger(__name__)

        self._appFrame:            SizedFrame     = cast(SizedFrame, None)
        self._demoComponentsPanel: DemoComponents = cast(DemoComponents, None)

        super().__init__(redirect)

    def OnInit(self):

        frameStyle:     int           = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT

        self._appFrame = SizedFrame(parent=None, title="Test UI Components", size=(FRAME_WIDTH, FRAME_HEIGHT), style=frameStyle)
        self._appFrame.CreateStatusBar()  # should always do this when there's a resize border

        sizedPanel: SizedPanel = self._appFrame.GetContentsPane()

        self._demoComponentsPanel = DemoComponentsPanel(parent=sizedPanel)
        # noinspection PyUnresolvedReferences
        self._demoComponentsPanel.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()

        self.SetTopWindow(self._appFrame)

        self._appFrame.Show(True)

        return True

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu = Menu()
        viewMenu: Menu = Menu()

        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")

        viewMenu.AppendSeparator()
        menuBar.Append(fileMenu, 'File')
        menuBar.Append(viewMenu, 'View')

        self._appFrame.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)


if __name__ == "__main__":

    UnitTestBase.setUpLogging()

    testApp: DemoComponents = DemoComponents(redirect=False)

    testApp.MainLoop()
