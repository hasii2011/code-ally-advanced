
from logging import Logger
from logging import getLogger

from wx import Choice
from wx import ID_ANY
from wx import StaticLine

from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase

from tests.demo.DemoStepId import DemoStepId


class SelectionStep(MysticStepBase):

    TITLE_FONT_SIZE: int = 18
    TITLE:           str = 'Selection Step'

    def __init__(self, parent: SizedPanel):

        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent)

        self.SetSizerType('vertical')
        self.SetSizerProps(expand=True, proportion=1)      # noqa

        self._createPageTitle(SelectionStep.TITLE)

        demoStepIds = [s.value for s in DemoStepId]

        self._stepSelection: Choice = Choice(self, choices=demoStepIds)
        self._stepSelection.SetSizerProps(expand=True, proportion=1)

    def stepId(self) -> DemoStepId:
        idx:         int = self._stepSelection.GetSelection()
        arrangerStr: str = self._stepSelection.GetString(idx)

        return DemoStepId(arrangerStr)

    def _createPageTitle(self, title: str):
        """
        """
        self._createLabel(label=title, fontSize=SelectionStep.TITLE_FONT_SIZE)
        StaticLine(parent=self, id=ID_ANY)
