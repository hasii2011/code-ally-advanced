
from typing import List
from typing import cast
from typing import NewType
from typing import Callable

from logging import Logger
from logging import getLogger

from wx import OK
from wx import CANCEL
from wx import ID_ANY
from wx import CAPTION
from wx import ID_CANCEL
from wx import CLOSE_BOX
from wx import EVT_BUTTON
from wx import STAY_ON_TOP
from wx import BORDER_THEME

from wx import Size
from wx import Bitmap
from wx import Window
from wx import CommandEvent
from wx import StaticBitmap

from wx import NewIdRef as wxNewIdRef

from wx.lib.buttons import ThemedGenBitmapTextButton

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel


from codeallyadvanced.resources.mystic.cancel16 import embeddedImage as cancelButtonImage
from codeallyadvanced.resources.mystic.next16 import embeddedImage as nextButtonImage
from codeallyadvanced.resources.mystic.back16 import embeddedImage as backButtonImage

from codeallyadvanced.resources.mystic.MageBitMap import embeddedImage as mageImage

from codeallyadvanced.ui.mystic.MysticPanel import MysticPanel
from codeallyadvanced.ui.mystic.MysticStepBase import MysticStepBase

BUTTON_NEXT_TEXT:   str = 'Next'
BUTTON_BACK_TEXT:   str = 'Back'
BUTTON_CANCEL_TEXT: str = 'Cancel'
BUTTON_FINISH_TEXT: str = 'Finish'

MYSTIC_CANCELLED: int = wxNewIdRef()
MYSTIC_FINISHED:  int = wxNewIdRef()

MysticBaseSteps = NewType('MysticBaseSteps', List[MysticStepBase])

#
# The mystic passes the step that is currently transitioning
# It is up to the callback to determine either the next step
# or the previous step
ComputeNextStepCallback = Callable[[MysticStepBase], int]
ComputeBackStepCallback = Callable[[MysticStepBase], int]


class Mystic(SizedDialog):
    """
    This is the dialog that hosts the mystic (aka wizard)
    Peculiarities:

        * As noted below make the static image large and the dialog stays a fixed size
        * Also, the first page must be the largest for the entire dialog to display

    """

    def __init__(self,
                 parent: Window,
                 title: str,
                 nextCallback: ComputeNextStepCallback | None = None,
                 backCallback: ComputeBackStepCallback | None = None,
                 bitmap: Bitmap | None = None
                 ):
        """

        Args:
            parent:         The parent of the mystic
            title:          The mystic title
            nextCallback:   If present the mystic calls this method to compute the index
            of the next step
            backCallback:   If present the myst calls thsi method to compute the index
            of the previous step
            bitmap:     If present the mystic uses this image as the image to present
            during each mystic step.  If not present the mystic uses a bland image
            as a place holder
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=parent, title=title, style=CAPTION | STAY_ON_TOP | CLOSE_BOX)

        self._nextStepCallback: ComputeNextStepCallback | None = nextCallback
        self._backStepCallback: ComputeBackStepCallback | None = backCallback

        self._steps:            MysticBaseSteps = MysticBaseSteps([])
        self._stepNumber:       int       = 0
        self._wizardSuccessful: bool      = True

        # Outer panel holds buttons and side by side panel
        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(border=(["top", "bottom"], 10))

        self._horizontalPanel: SizedPanel = SizedPanel(parent=sizedPanel, style=BORDER_THEME)
        self._horizontalPanel.SetSizerType('horizontal')
        self._horizontalPanel.SetSizerProps(border=(["top", "bottom", "left", "right"], 20))

        self._btnCancel: ThemedGenBitmapTextButton = cast(ThemedGenBitmapTextButton, None)
        self._btnNext:   ThemedGenBitmapTextButton = cast(ThemedGenBitmapTextButton, None)
        self._btnBack:   ThemedGenBitmapTextButton = cast(ThemedGenBitmapTextButton, None)

        if bitmap is not None:
            self._bitMap: Bitmap = bitmap
        else:
            self._bitMap = mageImage.GetBitmap()

        # Making the bitmap large seems to keep the dialog a static size
        self._logo: StaticBitmap = StaticBitmap(
            parent=self._horizontalPanel,
            id=ID_ANY,
            bitmap=self._bitMap,    # noqa
            size=Size(width=100, height=200)
        )
        self._logo.SetSizerProps(proportion=1, halign='left', valign='center')

    @property
    def pageContainer(self) -> SizedPanel:
        """
        Client should parent their mage pages with this panel

        Returns:  The panel that should be the parent of all the mage's pages

        """
        return self._horizontalPanel

    def addMysticStep(self, mysticStep: MysticStepBase):
        """
        Add a step to the mystic;  Add them in the order you want
        to display them

        Args:
            mysticStep:
        """
        self._steps.append(mysticStep)

        mysticStep.Hide()
        self.Layout()

    def runMystic(self):

        self._layoutWizardButtons(parent=self.GetContentsPane())

        self._steps[self._stepNumber].Show()

        self.GetContentsPane().Layout()
        self.Fit()
        self.SetMinSize(self.GetSize())

        self._btnBack.Disable()

        ans = self.ShowModal()
        if ans == CANCEL:
            self.logger.info('Cancel pressed')
            return MYSTIC_CANCELLED
        else:
            return MYSTIC_FINISHED

    # noinspection PyUnusedLocal
    def _onCancel(self, event: CommandEvent):
        self._wizardSuccessful = False
        self.EndModal(CANCEL)

    # noinspection PyUnusedLocal
    def _onNext(self, event: CommandEvent):
        """
        Handle indicating that we are on last page, when we go past last page end the dialog

        Args:
            event:
        """

        oldPage: MysticStepBase = self._steps[self._stepNumber]
        if oldPage.validate() is False:
            return                  # Ugh.  short cut out

        oldPage.Hide()
        if self._nextStepCallback is not None:
            self._stepNumber = self._nextStepCallback(oldPage)
        else:
            self._stepNumber += 1

        pageCount: int = len(self._steps)

        if pageCount - 1 == self._stepNumber:
            self._btnNext.SetLabel(BUTTON_FINISH_TEXT)
        elif pageCount == self._stepNumber:
            self.EndModal(OK)
            return                  # Ugh.  short cut out

        self._btnBack.SetLabel(BUTTON_BACK_TEXT)
        self._btnBack.Enable()

        newPage: MysticStepBase = self._steps[self._stepNumber]
        newPage.Show()
        self.GetContentsPane().Layout()
        self._resizeMystic()

    # noinspection PyUnusedLocal
    def _onBack(self, event: CommandEvent):

        oldPage: MysticStepBase = self._steps[self._stepNumber]
        oldPage.Hide()

        if self._backStepCallback is not None:
            self._stepNumber = self._backStepCallback(oldPage)
        else:
            self._stepNumber -= 1

        if self._stepNumber == 0:
            self._btnBack.Disable()

        newPage: MysticStepBase = self._steps[self._stepNumber]
        newPage.Show()

        self.GetContentsPane().Layout()
        self._resizeMystic()
        self._btnNext.SetLabel(BUTTON_NEXT_TEXT)

    def _layoutWizardButtons(self, parent: SizedPanel):

        buttonPanel: SizedPanel = SizedPanel(parent)
        buttonPanel.SetSizerType('horizontal')
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        self._btnCancel = ThemedGenBitmapTextButton(buttonPanel, label=BUTTON_CANCEL_TEXT, bitmap=cancelButtonImage.GetBitmap(), id=ID_CANCEL)
        self._btnNext   = ThemedGenBitmapTextButton(buttonPanel, label=BUTTON_NEXT_TEXT,   bitmap=nextButtonImage.GetBitmap())
        self._btnBack   = ThemedGenBitmapTextButton(buttonPanel, label=BUTTON_BACK_TEXT,   bitmap=backButtonImage.GetBitmap(),)

        self._btnCancel.Bind(EVT_BUTTON, self._onCancel)
        self._btnNext.Bind(EVT_BUTTON,   self._onNext)
        self._btnBack.Bind(EVT_BUTTON,   self._onBack)

        self._btnNext.SetDefault()

    def _resizeMystic(self):
        """
        Run this after each step change and after the step layout
        """
        self.Fit()
        self.SetMinSize(self.GetSize())
