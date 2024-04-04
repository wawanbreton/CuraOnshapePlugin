# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Optional, List

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal

from UM.Logger import Logger

from .DocumentsModel import DocumentsModel

if TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply
    from ..data.DocumentsTreeNode import DocumentsTreeNode
    from ..api.OnshapeApi import OnshapeApi
    from ..data.BaseElement import BaseElement


class DocumentsItem(QObject):
    """Represents an item in the documents tree to be displayed and interacted with on the UI"""

    def __init__(self, node: "DocumentsTreeNode", api: "OnshapeApi", path: List[str]):
        super().__init__(parent = None)
        self._node: "DocumentsTreeNode" = node
        self._api: "OnshapeApi" = api
        self.element: "BaseElement" = self._node.element
        self._subModel: DocumentsModel = DocumentsModel(self._node, self._api, path)
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

    @pyqtProperty(str, notify = iconChanged)
    def icon(self) -> str:
        if self.element.hasThumbnail():
            if self._thumbnail_str_data is not None:
                return self._thumbnail_str_data
            else:
                if not self._thumbnail_downloaded:
                    self._thumbnail_downloaded = True
                    if self.element.thumbnail_url is not None:
                        self._api.loadThumbnail(self.element.thumbnail_url,
                                                self._onThumbnailReceived,
                                                self._onThumbnailError)
                return None
        else:
            return self.element.icon

    @pyqtProperty(bool, constant = True)
    def hasThumbnail(self) -> bool:
        return self.element.hasThumbnail()

    @pyqtProperty(bool, constant = True)
    def hasChildren(self) -> bool:
        return self.element.has_children

    @pyqtProperty(bool, constant = True)
    def isDownloadable(self) -> bool:
        return self.element.is_downloadable

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
