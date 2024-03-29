# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtNetwork import QNetworkRequest

from ..data.Root import Root

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkReply
    from ..data.DocumentsTreeNode import DocumentsTreeNode
    from ..api.OnshapeApi import OnshapeApi
    from ..DocumentsItem import DocumentsItem


class DocumentsModel(QObject):
    """Data model containing multiple DocumentsItem instances, to be displayed on the UI"""

    def __init__(self, node: "DocumentsTreeNode", api: "OnshapeApi", path: List[str]):
        super().__init__(parent = None)
        self._node: "DocumentsTreeNode" = node
        self._api: "OnshapeApi" = api
        self._items: List["DocumentsItem"] = []
        self._path: List[str] = path + [self._node.element.name]
        self._load_error: Optional[str] = None

        if self.loaded:
            self._updateItems()

    @pyqtProperty(list, constant = True)
    def path(self) -> List[str]:
        return self._path

    elementsChanged = pyqtSignal()

    @pyqtProperty(list, notify = elementsChanged)
    def elements(self) -> List["DocumentsItem"]:
        return self._items

    def _updateItems(self) -> None:
        from .DocumentsItem import DocumentsItem
        self._items = [DocumentsItem(child, self._api, self._path) for child in self._node.children]
        self.elementsChanged.emit()

        for item in self._items:
            item.selectedChanged.connect(self.selectedItemsChanged)

        self.selectedItemsChanged.emit()

    @pyqtProperty(bool, notify = elementsChanged)
    def loaded(self) -> bool:
        return self._node.children_loaded

    @pyqtProperty(bool, constant = True)
    def isRoot(self) -> bool:
        return isinstance(self._node.element, Root)

    errorChanged = pyqtSignal()

    @pyqtProperty(bool, notify = errorChanged)
    def hasError(self) -> bool:
        return self._load_error is not None

    @pyqtProperty(str, notify = errorChanged)
    def error(self) -> Optional[str]:
        return self._load_error

    @pyqtSlot()
    def load(self) -> None:
        def on_finished(children: List["DocumentsTreeNode"]):
            self._node.setChildren(children)
            self._updateItems()

        def on_error(request: "QNetworkReply", error: "QNetworkReply.NetworkError"):
            self._load_error = request.errorString() + bytes(request.readAll()).decode()
            self.errorChanged.emit()

        for item in self._items:
            item.selected = False

        if not self.loaded:
            self._node.element.loadChildren(self._api, on_finished, on_error)

    @pyqtProperty(bool, constant = True)
    def refreshable(self) -> bool:
        return self._node.element.is_refreshable

    def clear(self) -> None:
        self._items = []
        self._node.clear()
        self.elementsChanged.emit()

        self._load_error = None
        self.errorChanged.emit()

    @pyqtSlot()
    def refresh(self) -> None:
        self.clear()
        self.load()

    selectedItemsChanged = pyqtSignal()

    @pyqtProperty(list, notify = selectedItemsChanged)
    def selectedItems(self) -> List["DocumentsItem"]:
        return [item for item in self._items if item.selected]
