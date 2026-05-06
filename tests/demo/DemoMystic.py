
from typing import Dict
from typing import cast
from typing import NewType

from logging import Logger
from logging import getLogger

from wx import EVT_BUTTON
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT

from wx import App
from wx import Button
from wx import CommandEvent

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from codeallyadvanced.ui.mystic.Mystic import Mystic
from codeallyadvanced.ui.mystic.Mystic import MYSTIC_CANCELLED
from codeallyadvanced.ui.mystic.Mystic import MYSTIC_FINISHED
from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase

from tests.demo.DemoStep import DemoStep
from tests.demo.DemoStepId import DemoStepId
from tests.demo.SelectionStep import SelectionStep

FRAME_WIDTH:  int = 400
FRAME_HEIGHT: int = 300

StepMap = NewType('StepMap', Dict[DemoStepId, DemoStep | SelectionStep])


INTRO_STEP_IDX:     int = 0
SELECTION_STEP_IDX: int = 1

class DemoPanel(SizedPanel):

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

        mystic: Mystic  = Mystic(parent=self, title='', nextCallback=self._getNextStep, backCallback=self._getBackStep)

        # Intro page is step/page 0
        introStep:     DemoStep = DemoStep(parent=mystic.pageContainer, title='Introduction', demoText='Demo Introduction Step', stepId=DemoStepId.NextStep, stepNumber=0)
        selectionStep: SelectionStep = SelectionStep(parent=mystic.pageContainer)
        secondStep:    DemoStep = DemoStep(parent=mystic.pageContainer, title='Second Step', demoText='Demo Second Step', stepId=DemoStepId.SecondStep, stepNumber=2)
        thirdStep:     DemoStep = DemoStep(parent=mystic.pageContainer, title='Third Step', demoText='Demo Third Step',   stepId=DemoStepId.ThirdStep,  stepNumber=3)
        fourthStep:    DemoStep = DemoStep(parent=mystic.pageContainer, title='Fourth Step', demoText='Demo Fourth Step', stepId=DemoStepId.FourthStep, stepNumber=4)

        mystic.addMysticStep(mysticStep=introStep)
        mystic.addMysticStep(mysticStep=selectionStep)
        mystic.addMysticStep(mysticStep=secondStep)
        mystic.addMysticStep(mysticStep=thirdStep)
        mystic.addMysticStep(mysticStep=fourthStep)

        self._selectionStep: SelectionStep = selectionStep

        self._stepMap: StepMap = StepMap(
            {
                DemoStepId.SelectionStep: selectionStep,
                DemoStepId.SecondStep:    secondStep,
                DemoStepId.ThirdStep:     thirdStep,
                DemoStepId.FourthStep:    fourthStep
            }
        )
        status: int = mystic.runMystic()

        if status == MYSTIC_CANCELLED:
            self._cancelCallback()
        elif status == MYSTIC_FINISHED:
            self._completeCallback()

    def _getNextStep(self, currentStep: MysticStepBase) -> int:

        if isinstance(currentStep, DemoStep):   # the Intro Step
            return currentStep.stepNumber + 1

        selectedStep: DemoStepId = self._selectionStep.stepId()

        return self._stepMap[selectedStep].stepNumber

    # noinspection PyUnusedLocal
    def _getBackStep(self, currentStep: MysticStepBase) -> int:
        if isinstance(currentStep, SelectionStep):
            return INTRO_STEP_IDX
        return SELECTION_STEP_IDX

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
