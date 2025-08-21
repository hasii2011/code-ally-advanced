
from typing import cast

from logging import Logger
from logging import getLogger

from wx import App
from wx import Bitmap
from wx import BitmapButton
from wx import DEFAULT_FRAME_STYLE
from wx import DefaultSize
from wx import FRAME_FLOAT_ON_PARENT
from wx import GridSizer
from wx import MiniFrame

from wx import NewIdRef as wxNewIdRef
from wx import Size
from wx.lib.embeddedimage import PyEmbeddedImage

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

# from codeallyadvanced.resources.umldiagrammer.Embedded64 import Actor as Actor64
# from codeallyadvanced.resources.umldiagrammer.Embedded64 import Aggregation as Aggregation64
#
# from codeallyadvanced.resources.umldiagrammer.Embedded32 import Actor as Actor32
# from codeallyadvanced.resources.umldiagrammer.Embedded32 import Aggregation as Aggregation32

from codeallybasic.UnitTestBase import UnitTestBase

FRAME_WIDTH:  int = 400
FRAME_HEIGHT: int = 300

JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfig.json"
TEST_DIRECTORY:               str = 'tests'

RESOURCES_PACKAGE_NAME: str = 'tests.resources'

class DemoPanel(SizedPanel):

    TOOLBOX_V_GAP:       int = 2
    TOOLBOX_H_GAP:       int = 2

    def __init__(self, parent, ):
        super().__init__(parent=parent)

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self._layoutExtraLargeIcons()
        self._layoutLargeIcons()
        self._layoutMediumIcons()
        self._layoutSmallIcons()

    def _layoutExtraLargeIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded64

        extraLargeContainer: SizedStaticBox = SizedStaticBox(self, label='Extra Large Icons')
        extraLargeContainer.SetSizerType('horizontal')
        extraLargeContainer.SetSizerProps(expand=True, proportion=1)

        for embedded in dir(codeallyadvanced.resources.umldiagrammer.Embedded64):
            if not embedded.startswith("__"):
                print(f'{embedded=}')
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded64, embedded)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp = pyEmbeddedImage.GetBitmap()
                    BitmapButton(parent=extraLargeContainer, id=wxNewIdRef(), bitmap=bmp, size=DefaultSize)

    def _layoutLargeIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded32

        largeContainer: SizedStaticBox = SizedStaticBox(self, label='Large Icons')
        largeContainer.SetSizerType('horizontal')
        largeContainer.SetSizerProps(expand=True, proportion=1)
        for embedded in dir(codeallyadvanced.resources.umldiagrammer.Embedded32):
            if not embedded.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded32, embedded)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp = pyEmbeddedImage.GetBitmap()
                    BitmapButton(parent=largeContainer, id=wxNewIdRef(), bitmap=bmp, size=DefaultSize)

    def _layoutMediumIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded24

        mediumContainer: SizedStaticBox = SizedStaticBox(self, label='Medium Icons')
        mediumContainer.SetSizerType('horizontal')
        mediumContainer.SetSizerProps(expand=True, proportion=1)
        for embedded in dir(codeallyadvanced.resources.umldiagrammer.Embedded24):
            if not embedded.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded24, embedded)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp = pyEmbeddedImage.GetBitmap()
                    BitmapButton(parent=mediumContainer, id=wxNewIdRef(), bitmap=bmp, size=DefaultSize)

    def _layoutSmallIcons(self):
        import codeallyadvanced.resources.umldiagrammer.Embedded16

        smallContainer: SizedStaticBox = SizedStaticBox(self, label='Small Icons')
        smallContainer.SetSizerType('horizontal')
        smallContainer.SetSizerProps(expand=True, proportion=1)

        for embedded in dir(codeallyadvanced.resources.umldiagrammer.Embedded16):
            if not embedded.startswith("__"):
                pyEmbeddedImage: PyEmbeddedImage = getattr(codeallyadvanced.resources.umldiagrammer.Embedded16, embedded)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp = pyEmbeddedImage.GetBitmap()
                    BitmapButton(parent=smallContainer, id=wxNewIdRef(), bitmap=bmp, size=DefaultSize)

class DemoIcons(App):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._appFrame: SizedFrame = cast(SizedFrame, None)
        self._demoFrame: DemoPanel = cast(DemoPanel, None)

        super().__init__(redirect=False)

    def OnInit(self):

        frameStyle:     int           = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT

        self._appFrame = SizedFrame(parent=None, title="Test Icons", size=(FRAME_WIDTH, FRAME_HEIGHT), style=frameStyle)
        self._appFrame.CreateStatusBar()  # should always do this when there's a resize border

        sizedPanel: SizedPanel = self._appFrame.GetContentsPane()

        self._demoFrame = DemoPanel(parent=sizedPanel)
        self._demoFrame.Fit()
        self._demoFrame.SetMinSize(self._demoFrame.GetSize())

        self.SetTopWindow(self._appFrame)

        self._appFrame.Show(True)

        return True


if __name__ == "__main__":

    UnitTestBase.setUpLogging()

    testApp: DemoIcons = DemoIcons()

    testApp.MainLoop()
