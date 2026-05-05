
from typing import cast

from logging import Logger
from logging import getLogger

from wx import App
from wx import Button
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import CommandEvent
from wx import EVT_BUTTON

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from codeallyadvanced.ui.mystic.Mystic import MYSTIC_CANCELLED
from codeallyadvanced.ui.mystic.Mystic import MYSTIC_FINISHED
from codeallyadvanced.ui.mystic.Mystic import Mystic

from tests.demo.DemoStep import DemoStep

FRAME_WIDTH:  int = 400
FRAME_HEIGHT: int = 300

class DemoPanel(SizedPanel):

    TOOLBOX_V_GAP:       int = 2
    TOOLBOX_H_GAP:       int = 2

    def __init__(self, parent, ):
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent)

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)
        Button(parent=self, label='Start Mystic')

        self.Bind(EVT_BUTTON, self._startMystic)

    # noinspection PyUnusedLocal
    def _startMystic(self, event: CommandEvent):

        mystic: Mystic  = Mystic(parent=self, title='')

        introPage:  DemoStep = DemoStep(parent=mystic.pageContainer, title='Introduction', demoText='Demo Introduction Step')
        secondPage: DemoStep = DemoStep(parent=mystic.pageContainer, title='Second Step', demoText='Demo Second Step')
        thirdPage:  DemoStep = DemoStep(parent=mystic.pageContainer, title='Third Step',  demoText='Demo Third Step')
        finalPage:  DemoStep = DemoStep(parent=mystic.pageContainer, title='Final Step',  demoText='Demo Final Step')

        mystic.addMysticPage(mysticPage=introPage)
        mystic.addMysticPage(mysticPage=secondPage)
        mystic.addMysticPage(mysticPage=thirdPage)
        mystic.addMysticPage(mysticPage=finalPage)

        status: int = mystic.runWizard()

        if status == MYSTIC_CANCELLED:
            self._cancelCallback()
        elif status == MYSTIC_FINISHED:
            self._completeCallback()

    def _cancelCallback(self):
        self.logger.info(f'Mystic Canceled')

    def _completeCallback(self):
        self.logger.info(f'Things are cool')


class DemoMystic(App):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._appFrame: SizedFrame = cast(SizedFrame, None)
        self._demoFrame: DemoPanel = cast(DemoPanel, None)

        super().__init__(redirect=False)

    def OnInit(self):

        frameStyle:     int           = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT

        self._appFrame = SizedFrame(parent=None, title="Test Mystic", size=(FRAME_WIDTH, FRAME_HEIGHT), style=frameStyle)
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

    testApp: DemoMystic = DemoMystic()

    testApp.MainLoop()
