
from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import StaticLine
from wx import StaticText

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase
from tests.demo.DemoStepId import DemoStepId


class DemoStep(MysticStepBase):

    TITLE_FONT_SIZE: int = 18

    TITLE: str = 'Second Step'

    MORE_TEXT: str = """
        Demo Second Step
    """

    def __init__(self, parent: SizedPanel, title: str, demoText: str, stepId: DemoStepId):

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent)

        self.SetSizerType('vertical')
        self.SetSizerProps(expand=True, proportion=1)      # noqa

        self._createPageTitle(title)
        StaticText(parent=self, id=ID_ANY, label=demoText)

        self._stepId:     DemoStepId = stepId

    @property
    def stepId(self) -> DemoStepId:
        return self._stepId

    def _createPageTitle(self, title: str):
        """
        """
        self._createLabel(label=title, fontSize=DemoStep.TITLE_FONT_SIZE)
        StaticLine(parent=self, id=ID_ANY)
