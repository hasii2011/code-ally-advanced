
from logging import Logger
from logging import getLogger

from pathlib import Path
from typing import Callable

from wx import BORDER_THEME
from wx import ID_ANY
from wx import ID_OK
from wx import DD_DEFAULT_STYLE
from wx import EVT_BUTTON
from wx import ART_BUTTON
from wx import ART_FOLDER

from wx import ArtProvider
from wx import BitmapBundle
from wx import BitmapButton
from wx import DirDialog
from wx import CommandEvent
from wx import Size
from wx import TextCtrl

from wx.lib.sized_controls import SizedPanel

DEFAULT_MIN_WIDTH:      int  = 280
DEFAULT_MAX_WIDTH:      int  = 600
DEFAULT_CONTROL_HEIGHT: int  = 36
FOLDER_BITMAP_SIZE:     Size = Size(16, 16)

DirectoryPathChangedCallback = Callable[[Path], None]

CALLBACK_PARAMETER = 'pathChangedCallback'


class DirectorySelector(SizedPanel):
    """
    A horizontal row container used for selecting and displaying a filesystem directory.

    Combines a non-editable TextCtrl showing the current directory path with a
    BitmapButton featuring a folder icon. Clicking the button
    invokes a DirDialog allowing the user to browse for a directory.

    Features:
        * Responsive layout: Horizontally expands (proportion=1) to fill available
          width in parent sizers, bounded by DEFAULT_MIN_WIDTH and
          DEFAULT_MAX_WIDTH.
        * Vertical alignment: Maintains a compact, single-line height
          (DEFAULT_CONTROL_HEIGHT) with centered controls.
        * Callback notification: Dispatches directory change events to an optional
          callback (`pathChangedCallback`) whenever a new directory is selected.
        * Two-way path binding: Provides a `directoryPath` property (getter/setter)
          to read or programmatically update the selected Path.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the DirectorySelector panel and controls.

        Extracts the optional 'pathChangedCallback' keyword argument before
        forwarding all remaining positional and keyword arguments to SizedPanel.

        Keyword Args:
            pathChangedCallback (DirectoryPathChangedCallback, optional): A callable
                accepting a `pathlib.Path` instance, invoked when the user selects a
                new directory via the browse dialog. Defaults to None.
            *args: Positional arguments forwarded to SizedPanel (e.g. parent).
            **kwargs: Keyword arguments forwarded to SizedPanel.
        """

        self.logger: Logger = getLogger(__name__)

        self._directorPathChangedCallback: DirectoryPathChangedCallback | None = kwargs.get(CALLBACK_PARAMETER, None)
        if self._directorPathChangedCallback is not None:
            kwargs.pop(CALLBACK_PARAMETER)

        super().__init__(style=BORDER_THEME, *args, **kwargs)

        self.SetSizerType('horizontal')
        self.SetSizerProps(expand=True, proportion=0)

        textCtrl: TextCtrl = TextCtrl(self)
        textCtrl.SetSizerProps(valign='centre', proportion=1, border=(('right',), 5))

        folderBitmapBundle: BitmapBundle = ArtProvider.GetBitmapBundle(ART_FOLDER, ART_BUTTON, FOLDER_BITMAP_SIZE)
        selectButton:       BitmapButton = BitmapButton(self, ID_ANY, folderBitmapBundle)
        selectButton.SetSizerProps(valign='centre')

        textCtrl.SetValue('')
        textCtrl.SetEditable(False)

        self._textDiagramsDirectory = textCtrl
        self._directoryPath:       Path = Path('')

        self.Bind(EVT_BUTTON, self._onSelectDiagramsDirectory, selectButton)

        self.SetMinSize(Size(DEFAULT_MIN_WIDTH, DEFAULT_CONTROL_HEIGHT))
        self.SetMaxSize(Size(DEFAULT_MAX_WIDTH, -1))

    def DoGetBestSize(self) -> Size:
        """
        Calculate the best size for this directory selector row.
        """
        return Size(400, DEFAULT_CONTROL_HEIGHT)

    @property
    def directoryPath(self) -> Path:
        return self._directoryPath

    @directoryPath.setter
    def directoryPath(self, value: Path):

        self._directoryPath = value
        self._textDiagramsDirectory.SetValue(str(value))

    # noinspection PyUnusedLocal
    def _onSelectDiagramsDirectory(self, _event: CommandEvent):

        with DirDialog(None, 'Choose the Diagrams Directory', defaultPath=str(self._directoryPath), style=DD_DEFAULT_STYLE) as dlg:

            if dlg.ShowModal() == ID_OK:
                self._directoryPath = Path(dlg.GetPath())
                self._textDiagramsDirectory.SetValue(str(self._directoryPath))
                if self._directorPathChangedCallback is not None:
                    self._directorPathChangedCallback(self._directoryPath)
