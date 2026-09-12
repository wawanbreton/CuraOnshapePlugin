# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QObject, QAbstractListModel, QModelIndex, Qt

from UM.Logger import Logger
from ..data.DocumentsTreeNode import DocumentsTreeNode
from ..data.SearchResult import SearchResult

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkReply
    from ..api.OnshapeApi import OnshapeApi
    from ..DocumentsItem import DocumentsItem


class DocumentsModel(QAbstractListModel):
    """Data model containing multiple DocumentsItem instances, to be displayed on the UI"""

    ModelDataRole = Qt.ItemDataRole.UserRole

    def __init__(self, node: "DocumentsTreeNode", api: "OnshapeApi", path: List[str]):
        super().__init__(parent = None)
        self._node: "DocumentsTreeNode" = node
        self._api: "OnshapeApi" = api
        self._items: List["DocumentsItem"] = []
        self._path: List[str] = path + [self._node.element.name]
        self._load_error: Optional[str] = None
        self._search_model: Optional["DocumentsModel"] = None
        self._is_loading_next_page: bool = False
        self._url_load_next_page: Optional[str] = None
        self._request_body: Optional[str] = None

        if self.loaded:
            self._updateItems()

    @pyqtSlot()
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        if role == self.ModelDataRole:
            return self._items[index.row()]
        return None

    def roleNames(self) -> dict:
        return { self.ModelDataRole: b'modelData' }

    @pyqtProperty(list, constant = True)
    def path(self) -> List[str]:
        return self._path

    def _updateItems(self) -> None:
        """Replaces the entire item list (used for the initial load and clear)."""
        from .DocumentsItem import DocumentsItem
        self.beginResetModel()
        self._items = [DocumentsItem(child, self._api, self._path) for child in self._node.children]
        self.endResetModel()

        for item in self._items:
            item.selectedChanged.connect(self.selectedItemsChanged)

        self.selectedItemsChanged.emit()

    def _appendItems(self, new_children: List["DocumentsTreeNode"]) -> None:
        """Appends new items at the end of the list without resetting the view."""
        from .DocumentsItem import DocumentsItem
        first = len(self._items)
        new_items = [DocumentsItem(child, self._api, self._path) for child in new_children]

        self.beginInsertRows(QModelIndex(), first, first + len(new_items) - 1)
        self._items.extend(new_items)
        self.endInsertRows()

        for item in new_items:
            item.selectedChanged.connect(self.selectedItemsChanged)

        self.selectedItemsChanged.emit()

    loadedChanged = pyqtSignal()

    @pyqtProperty(bool, notify = loadedChanged)
    def loaded(self) -> bool:
        return self._node.children_loaded

    errorChanged = pyqtSignal()

    @pyqtProperty(bool, notify = errorChanged)
    def hasError(self) -> bool:
        return self._load_error is not None

    @pyqtProperty(str, notify = errorChanged)
    def error(self) -> Optional[str]:
        return self._load_error

    hasMorePagesChanged = pyqtSignal()

    @pyqtProperty(bool, notify = hasMorePagesChanged)
    def hasMorePages(self) -> bool:
        return self._url_load_next_page is not None

    def _setUrlLoadNextPage(self, url_load_next_page: Optional[str]):
        if url_load_next_page != self._url_load_next_page:
            self._url_load_next_page = url_load_next_page
            self.hasMorePagesChanged.emit()

    isLoadingNextPageChanged = pyqtSignal()

    @pyqtProperty(bool, notify = isLoadingNextPageChanged)
    def isLoadingNextPage(self) -> bool:
        return self._is_loading_next_page

    def _setIsLoadingNextPage(self, value: bool) -> None:
        if value != self._is_loading_next_page:
            self._is_loading_next_page = value
            self.isLoadingNextPageChanged.emit()

    @pyqtSlot()
    def load(self) -> None:
        def on_finished(children: List["DocumentsTreeNode"], url_load_next_page: Optional[str], request_body: Optional[str]):
            self._node.setChildren(children)
            self._setUrlLoadNextPage(url_load_next_page)
            self._request_body = request_body
            self.loadedChanged.emit()
            self._updateItems()

        def on_error(request: "QNetworkReply", error: "QNetworkReply.NetworkError"):
            self._load_error = request.errorString() + bytes(request.readAll()).decode()
            self.errorChanged.emit()

        for item in self._items:
            item.selected = False

        if not self.loaded:
            self._node.element.loadChildren(self._api, on_finished, on_error)

    @pyqtSlot()
    def loadNextPage(self) -> None:
        """Loads the next page of items and appends them to the existing list"""
        if self._url_load_next_page is None or self._is_loading_next_page:
            return

        self._setIsLoadingNextPage(True)

        def on_finished(new_children: List["DocumentsTreeNode"], url_load_next_page: Optional[str], request_body: Optional[str]):
            for child in new_children:
                self._node.addChild(child)

            self._setUrlLoadNextPage(url_load_next_page)
            self._request_body = request_body
            self._setIsLoadingNextPage(False)
            self._appendItems(new_children)

        def on_error(request: "QNetworkReply", error: "QNetworkReply.NetworkError"):
            self._setIsLoadingNextPage(False)
            self._load_error = request.errorString() + bytes(request.readAll()).decode()
            self.errorChanged.emit()

        self._api.loadElements(self._url_load_next_page, on_finished, on_error, self._request_body)

    def clear(self) -> None:
        self.beginResetModel()
        self._items = []
        self._node.clear()
        self._next_page_offset = 0
        self.endResetModel()

        self._setUrlLoadNextPage(None)
        self._setIsLoadingNextPage(False)
        self._request_body = None

        self._load_error = None
        self.errorChanged.emit()
        self.loadedChanged.emit()

    @pyqtSlot()
    def refresh(self) -> None:
        self.clear()
        self.load()

    selectedItemsChanged = pyqtSignal()

    @pyqtProperty(list, notify = selectedItemsChanged)
    def selectedItems(self) -> List["DocumentsItem"]:
        return [item for item in self._items if item.selected]

    @pyqtSlot(result = bool)
    def isSearchModel(self) -> bool:
        return isinstance(self._node.element, SearchResult)

    @pyqtSlot(str, result = QObject)
    def searchModel(self, search_query: str) -> "DocumentsModel":
        self._search_model = DocumentsModel(DocumentsTreeNode(SearchResult(search_query, self._node.element)), self._api, self._path)
        return self._search_model

    @pyqtSlot(str)
    def newSearch(self, search_query: str) -> None:
        self._node.element.search_query = search_query
        self.refresh()

    @pyqtProperty(bool, constant = True)
    def isSearchable(self) -> bool:
        return self._node.element.is_searchable
