
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

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from codeallyadvanced.resources.images.icons.embedded32.UmlLollipop import embeddedImage as imageLollipop32
from codeallyadvanced.resources.images.icons.embedded16.UmlLollipop import embeddedImage as imageLollipop16

from codeallyadvanced.resources.images.icons.embedded32.UmlNote import embeddedImage as imageUmlNote32
from codeallyadvanced.resources.images.icons.embedded16.UmlNote import embeddedImage as imageUmlNote16

from codeallyadvanced.resources.images.icons.embedded32.UmlText import embeddedImage as imageUmlText32
from codeallyadvanced.resources.images.icons.embedded16.UmlText import embeddedImage as imageUmlText16

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

        largeContainer: SizedStaticBox = SizedStaticBox(self, label='Large Icons')
        smallContainer: SizedStaticBox = SizedStaticBox(self, label='Small Icons')

        largeContainer.SetSizerType('horizontal')
        smallContainer.SetSizerType('horizontal')

        largeContainer.SetSizerProps(expand=True, proportion=1)
        smallContainer.SetSizerProps(expand=True, proportion=1)

        bitmapLollipop32: Bitmap = imageLollipop32.GetBitmap()
        bitmapLollipop16: Bitmap = imageLollipop16.GetBitmap()

        bitmapUmlNote32: Bitmap = imageUmlNote32.GetBitmap()
        bitmapUmlNote16: Bitmap = imageUmlNote16.GetBitmap()

        bitmapUmlText32: Bitmap = imageUmlText32.GetBitmap()
        bitmapUmlText16: Bitmap = imageUmlText16.GetBitmap()

        BitmapButton(parent=largeContainer, id=wxNewIdRef(), bitmap=bitmapLollipop32, size=DefaultSize)
        BitmapButton(parent=smallContainer, id=wxNewIdRef(), bitmap=bitmapLollipop16, size=DefaultSize)

        BitmapButton(parent=largeContainer, id=wxNewIdRef(), bitmap=bitmapUmlNote32, size=DefaultSize)
        BitmapButton(parent=smallContainer, id=wxNewIdRef(), bitmap=bitmapUmlNote16, size=DefaultSize)

        BitmapButton(parent=largeContainer, id=wxNewIdRef(), bitmap=bitmapUmlText32, size=DefaultSize)
        BitmapButton(parent=smallContainer, id=wxNewIdRef(), bitmap=bitmapUmlText16, size=DefaultSize)


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
