# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Optional, List

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from UM.Logger import Logger

from .DocumentsModel import DocumentsModel
from ..data.Part import Part

if TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply
    from ..data.DocumentsTreeNode import DocumentsTreeNode
    from ..api.OnshapeApi import OnshapeApi
    from ..data.BaseElement import BaseElement


class DocumentsItem(QObject):
    """Represents an item in the documents tree to be displayed and interacted with on the UI"""

    def __init__(self, node: "DocumentsTreeNode", api: "OnshapeApi", path: List[str], parent_model: "DocumentsModel"):
        super().__init__(parent = None)
        self._node: "DocumentsTreeNode" = node
        self._api: "OnshapeApi" = api
        self.element: "BaseElement" = self._node.element
        self._subModel: DocumentsModel = DocumentsModel(self._node, self._api, path)
        self._parent_model: DocumentsModel = parent_model
        self._thumbnail_str_data: Optional[str] = None
        self._thumbnail_downloaded: bool = False
        self._selected: bool = False
        self._path: List[str] = path

    @pyqtProperty(str, constant = True)
    def name(self) -> str:
        return self.element.name

    iconChanged = pyqtSignal()

    def _onThumbnailReceived(self, data: "QByteArray") -> None:
        self._thumbnail_str_data = "data:image/png;base64,"
        self._thumbnail_str_data += bytes(data.toBase64()).decode('utf-8')
        self.iconChanged.emit()

    def _onThumbnailError(self, request: "QNetworkReply", error: "QNetworkReply.NetworkError") -> None:
        Logger.warning(f'Error when retrieving thumbnail: {error}')

    def _fetchThumbnail(self) -> None:
        if isinstance(self.element, Part) and self.element.configuration:
            def on_shaded_view_received(image_data: str) -> None:
                self._thumbnail_str_data = image_data
                self.iconChanged.emit()

            def on_shaded_view_error(request: "QNetworkReply", error: Optional["QNetworkReply.NetworkError"]) -> None:
                self.element.loadThumbnail(self._api, self._onThumbnailReceived, self._onThumbnailError)

            self._api.loadPartShadedView(
                self.element.document_id,
                self.element.workspace_id,
                self.element.tab_id,
                self.element.id,
                self.element.configuration,
                on_shaded_view_received,
                on_shaded_view_error
            )
        else:
            self.element.loadThumbnail(self._api, self._onThumbnailReceived, self._onThumbnailError)

    @pyqtProperty(str, notify = iconChanged)
    def icon(self) -> str:
        if self.element.hasThumbnail() or (isinstance(self.element, Part) and self.element.configuration):
            if self._thumbnail_str_data is not None:
                return self._thumbnail_str_data
            else:
                if not self._thumbnail_downloaded:
                    self._thumbnail_downloaded = True
                    self._fetchThumbnail()
                return None
        else:
            return self.element.icon

    @pyqtProperty(bool, constant = True)
    def hasThumbnail(self) -> bool:
        return self.element.hasThumbnail() or (isinstance(self.element, Part) and self.element.configuration is not None)

    @pyqtProperty(bool, constant = True)
    def hasChildren(self) -> bool:
        return self.element.has_children

    @pyqtProperty(bool, constant = True)
    def isDownloadable(self) -> bool:
        return self.element.is_downloadable

    @pyqtProperty(bool, constant = True)
    def hasConfigurationParameters(self) -> bool:
        return self.isDownloadable and self._parent_model.hasConfigurationParameters

    @pyqtProperty(list, constant = True)
    def configurationParameters(self) -> list:
        return self._parent_model.configurationParameters

    @pyqtProperty(str, constant = True)
    def shortDesc(self) -> str:
        return self.element.short_desc

    @pyqtProperty(str, constant = True)
    def lastModifiedDate(self) -> Optional[str]:
        if self.element.last_modified_date is not None:
            return self.element.last_modified_date.astimezone().strftime("%d-%m-%Y %H:%M")
        else:
            return None

    @pyqtProperty(str, constant = True)
    def lastModifiedBy(self) -> Optional[str]:
        if self.element.last_modified_by is not None:
            return self.element.last_modified_by
        else:
            return None

    @pyqtProperty(bool, constant = True)
    def settableAsDefault(self) -> bool:
        return self.element.settable_as_default

    @pyqtProperty(QObject, constant = True)
    def childModel(self) -> DocumentsModel:
        return self._subModel

    selectedChanged = pyqtSignal()

    def setSelected(self, selected: bool) -> None:
        self._selected = selected
        self.selectedChanged.emit()

    @pyqtProperty(bool, notify = selectedChanged, fset = setSelected)
    def selected(self) -> bool:
        return self._selected

    def getPath(self) -> List[str]:
        return self._path

    @pyqtSlot()
    def setAsDefault(self) -> None:
        self.element.setAsDefault()
