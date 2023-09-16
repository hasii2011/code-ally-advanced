

from wx import App
from wx import Frame
from wx import ID_ANY
from wx import ScrolledWindow

from hasiihelper.UnitTestBase import UnitTestBase


class DummyApp(App):
    def OnInit(self):
        return True


class UnitTestBaseW(UnitTestBase):
    """
    This base class is meant to be used by unit tests that need wx.App
    instance opened.
    """

    def setUp(self):
        super().setUp()

        self._app:   DummyApp = DummyApp()
        #  Create frame
        baseFrame: Frame = Frame(None, ID_ANY, "", size=(10, 10))
        # noinspection PyTypeChecker
        umlFrame = ScrolledWindow(baseFrame)
        umlFrame.Show(True)

        self._listeningWindow = umlFrame

    def tearDown(self):
        self._app.OnExit()
