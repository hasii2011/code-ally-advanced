
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from wx import DEFAULT_FRAME_STYLE
from wx import ID_EXIT

from wx import App
from wx import Menu
from wx import MenuBar

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from tests.demo.DemoComponentsFrame import DemoComponentsFrame


FRAME_WIDTH:  int = 800
FRAME_HEIGHT: int = 600

ZOOM_WIDTH:   int = FRAME_WIDTH - 100
ZOOM_HEIGHT:  int = FRAME_HEIGHT - 100

ZOOM_IN_UPPER_X: int = 0
ZOOM_IN_UPPER_Y: int = 0

ZOOM_OUT_X: int = ZOOM_WIDTH // 2
ZOOM_OUT_Y: int = ZOOM_HEIGHT // 2

INITIAL_X:   int = 100
INITIAL_Y:   int = 100

INCREMENT_X: int = INITIAL_X + 20
INCREMENT_Y: int = INITIAL_Y + 40

JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfig.json"
TEST_DIRECTORY:               str = 'tests'

RESOURCES_PACKAGE_NAME: str = 'tests.resources'


class DemoComponents(App):

    def __init__(self, redirect: bool):

        UnitTestBase.setUpLogging()

        self.logger:          Logger          = getLogger(__name__)

        self._frame:          SizedFrame   = cast(SizedFrame, None)
        self._diagramFrame:   DemoComponents = cast(DemoComponents, None)

        self._ID_DISPLAY_OGL_CLASS: int = wxNewIdRef()
        self._ID_DISPLAY_OGL_TEXT:  int = wxNewIdRef()
        self._ID_ZOOM_IN:           int = wxNewIdRef()
        self._ID_ZOOM_OUT:          int = wxNewIdRef()

        self._x: int = 100
        self._y: int = 100

        super().__init__(redirect)

    def OnInit(self):
        self._frame = SizedFrame(parent=None, title="Test Ogl Elements", size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE)
        self._frame.CreateStatusBar()  # should always do this when there's a resize border

        sizedPanel: SizedPanel = self._frame.GetContentsPane()
        self._diagramFrame = DemoComponentsFrame(parent=sizedPanel)
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()

        self.SetTopWindow(self._frame)

        self._frame.SetAutoLayout(True)
        self._frame.Show(True)

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

        self._frame.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)

    def _getPosition(self) -> Tuple[int, int]:
        x: int = self._x
        y: int = self._y

        self._x += INCREMENT_X
        self._y += INCREMENT_Y
        return x, y


testApp: DemoComponents = DemoComponents(redirect=False)

testApp.MainLoop()
