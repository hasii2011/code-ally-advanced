
from typing import cast
from types import ModuleType

from logging import Logger
from logging import getLogger

from importlib import import_module


from wx import App
from wx import BitmapButton

from wx import DEFAULT_FRAME_STYLE
from wx import DefaultSize
from wx import FRAME_FLOAT_ON_PARENT
from wx import MessageBox

from wx import NewIdRef as wxNewIdRef
from wx import OK

from wx.lib.embeddedimage import PyEmbeddedImage

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from click import command
from click import option
from click import version_option

from codeallybasic.UnitTestBase import UnitTestBase

FRAME_WIDTH:  int = 1900
FRAME_HEIGHT: int = 400

JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfig.json"
TEST_DIRECTORY:               str = 'tests'

EMBEDDED_PACKAGE_PREFIX: str = 'Embedded'

EXTRA_LARGE: str = f'{EMBEDDED_PACKAGE_PREFIX}64'
LARGE:       str = f'{EMBEDDED_PACKAGE_PREFIX}32'
MEDIUM:      str = f'{EMBEDDED_PACKAGE_PREFIX}24'
SMALL:       str = f'{EMBEDDED_PACKAGE_PREFIX}16'

__version__ = "2.0.0"

class NoSuchModuleException(Exception):
    pass


class DemoPanel(SizedPanel):

    def __init__(self, parent, imagePackage: str):
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self._layoutAllIcons(imagePackage=imagePackage)

    def _layoutAllIcons(self, imagePackage: str):

        for label, suffix in [
            ("Extra Large Icons", EXTRA_LARGE),
            ("Large Icons",       LARGE),
            ("Medium Icons",      MEDIUM),
            ("Small Icons",       SMALL)
        ]:
            container: SizedStaticBox = self._createContainer(label=label)
            moduleObj: ModuleType     = self._importModule(imagePackage=imagePackage, embeddedPackageName=suffix)

            self._createButtonIcons(moduleObj=moduleObj, container=container)

    def _createContainer(self, label: str) -> SizedStaticBox:

        container: SizedStaticBox = SizedStaticBox(self, label=label)
        container.SetSizerType('horizontal')

        container.SetSizerProps(expand=True, proportion=1)

        return container

    def _importModule(self, imagePackage: str, embeddedPackageName: str) -> ModuleType:

        moduleStr: str = f'{imagePackage}.{embeddedPackageName}'
        try:
            moduleObj: ModuleType = import_module(moduleStr)
        except ImportError:
            self.logger.error(f'Failed to import icon package: {moduleStr}')
            raise NoSuchModuleException(f'Failed to import icon package: {moduleStr}')

        return moduleObj

    def _createButtonIcons(self, moduleObj: ModuleType, container: SizedStaticBox):

        for embedded in dir(moduleObj):
            if not embedded.startswith("__"):
                # self.logger.info(f'{embedded=}')
                pyEmbeddedImage: PyEmbeddedImage = getattr(moduleObj, embedded)
                if isinstance(pyEmbeddedImage, PyEmbeddedImage):
                    bmp = pyEmbeddedImage.GetBitmap()
                    button: BitmapButton = BitmapButton(parent=container, id=wxNewIdRef(), bitmap=bmp, size=DefaultSize)
                    button.SetToolTip(embedded)


class DemoIcons(App):

    imagePackage: str = ''
    """
    Class variable because need to set it before class is instantiated
    """

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._appFrame: SizedFrame = cast(SizedFrame, None)
        self._demoFrame: DemoPanel = cast(DemoPanel, None)

        super().__init__(redirect=False)

    def OnInit(self):

        try:
            frameStyle: int = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT

            self._appFrame = SizedFrame(parent=None, title=DemoIcons.imagePackage, size=(FRAME_WIDTH, FRAME_HEIGHT), style=frameStyle)
            self._appFrame.CreateStatusBar()  # should always do this when there's a resize border

            sizedPanel: SizedPanel = self._appFrame.GetContentsPane()

            self._demoFrame = DemoPanel(parent=sizedPanel, imagePackage=DemoIcons.imagePackage)
            self._demoFrame.Fit()
            self._demoFrame.SetMinSize(self._demoFrame.GetSize())

            self.SetTopWindow(self._appFrame)

            self._appFrame.Show(True)

        except NoSuchModuleException as e:
            answer = MessageBox(f'{e}', "Error", OK)
            if answer == OK:
                pass

        return True

@command()
@version_option(version=f'{__version__}', message='%(version)s')
@option('-p', '--image-package', required=True, help='The base image package.')
def commandHandler(image_package: str):

    UnitTestBase.setUpLogging()

    print(f'{image_package=}')
    DemoIcons.imagePackage = image_package      # Set the class variable before instantiation

    testApp: DemoIcons = DemoIcons()
    testApp.MainLoop()


if __name__ == "__main__":
    commandHandler()
