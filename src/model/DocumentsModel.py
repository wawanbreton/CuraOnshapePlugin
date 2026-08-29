# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, List, Optional

from PyQt6.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QAbstractListModel, QModelIndex, Qt
from PyQt6.QtNetwork import QNetworkRequest

from ..data.Root import Root

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkReply
    from ..data.DocumentsTreeNode import DocumentsTreeNode
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
        self._has_more_pages: bool = False
        self._is_loading_next_page: bool = False
        self._next_page_offset: int = 0

        if self.loaded:
            self._updateItems()

    # ── QAbstractListModel interface ─────────────────────────────────────────

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
        return {self.ModelDataRole: b'modelData'}

    # ── Path property ─────────────────────────────────────────────────────────

    @pyqtProperty(list, constant = True)
    def path(self) -> List[str]:
        return self._path

    # ── Internal item management ──────────────────────────────────────────────

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

    # ── Loaded / root state ───────────────────────────────────────────────────

    loadedChanged = pyqtSignal()

    @pyqtProperty(bool, notify = loadedChanged)
    def loaded(self) -> bool:
        return self._node.children_loaded

    @pyqtProperty(bool, constant = True)
    def isRoot(self) -> bool:
        return isinstance(self._node.element, Root)

    # ── Error state ───────────────────────────────────────────────────────────

    errorChanged = pyqtSignal()

    @pyqtProperty(bool, notify = errorChanged)
    def hasError(self) -> bool:
        return self._load_error is not None

    @pyqtProperty(str, notify = errorChanged)
    def error(self) -> Optional[str]:
        return self._load_error

    # ── Pagination state ──────────────────────────────────────────────────────

    hasMorePagesChanged = pyqtSignal()

    @pyqtProperty(bool, notify = hasMorePagesChanged)
    def hasMorePages(self) -> bool:
        return self._has_more_pages

    def _setHasMorePages(self, value: bool) -> None:
        if value != self._has_more_pages:
            self._has_more_pages = value
            self.hasMorePagesChanged.emit()

    isLoadingNextPageChanged = pyqtSignal()

    @pyqtProperty(bool, notify = isLoadingNextPageChanged)
    def isLoadingNextPage(self) -> bool:
        return self._is_loading_next_page

    def _setIsLoadingNextPage(self, value: bool) -> None:
        if value != self._is_loading_next_page:
            self._is_loading_next_page = value
            self.isLoadingNextPageChanged.emit()

    # ── Load / next-page / refresh ────────────────────────────────────────────

    @pyqtSlot()
    def load(self) -> None:
        def on_finished(children: List["DocumentsTreeNode"]):
            self._node.setChildren(children)
            self.loadedChanged.emit()
            self._updateItems()

        def on_finished_paged(children: List["DocumentsTreeNode"], has_more: bool, document_count: int):
            self._node.setChildren(children)
            self._next_page_offset = document_count
            self.loadedChanged.emit()
            self._setHasMorePages(has_more)
            self._updateItems()

        def on_error(request: "QNetworkReply", error: "QNetworkReply.NetworkError"):
            self._load_error = request.errorString() + bytes(request.readAll()).decode()
            self.errorChanged.emit()

        for item in self._items:
            item.selected = False

        if not self.loaded:
            if isinstance(self._node.element, Root):
                self._node.element.loadChildrenPage(self._api, 0, on_finished_paged, on_error)
            else:
                self._node.element.loadChildren(self._api, on_finished, on_error)

    @pyqtSlot()
    def loadNextPage(self) -> None:
        """Loads the next page of items and appends them to the existing list"""
        if not self._has_more_pages or self._is_loading_next_page:
            return

        self._setIsLoadingNextPage(True)

        def on_finished(new_children: List["DocumentsTreeNode"], has_more: bool, document_count: int):
            for child in new_children:
                self._node.addChild(child)

            self._next_page_offset += document_count
            self._setIsLoadingNextPage(False)
            self._setHasMorePages(has_more)
            self._appendItems(new_children)

        def on_error(request: "QNetworkReply", error: "QNetworkReply.NetworkError"):
            self._setIsLoadingNextPage(False)
            self._load_error = request.errorString() + bytes(request.readAll()).decode()
            self.errorChanged.emit()

        self._node.element.loadChildrenPage(self._api, self._next_page_offset, on_finished, on_error)

    @pyqtProperty(bool, constant = True)
    def refreshable(self) -> bool:
        return self._node.element.is_refreshable

    def clear(self) -> None:
        self.beginResetModel()
        self._items = []
        self._node.clear()
        self._next_page_offset = 0
        self.endResetModel()

        self._setHasMorePages(False)
        self._setIsLoadingNextPage(False)

        self._load_error = None
        self.errorChanged.emit()
        self.loadedChanged.emit()

        if isinstance(self._node.element, Root):
            self._node.element.resetStorage()

    @pyqtSlot()
    def refresh(self) -> None:
        self.clear()
        self.load()

    # ── Selected items ────────────────────────────────────────────────────────

    selectedItemsChanged = pyqtSignal()

    @pyqtProperty(list, notify = selectedItemsChanged)
    def selectedItems(self) -> List["DocumentsItem"]:
        return [item for item in self._items if item.selected]

