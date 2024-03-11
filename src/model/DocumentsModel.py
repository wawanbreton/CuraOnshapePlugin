# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QObject

from ..data.Root import Root


class DocumentsModel(QObject):

    def __init__(self, node, api, path):
        super().__init__(parent = None)
        self._node = node
        self._api = api
        self._items = []
        self._path = path + [self._node.element.name]
        self._load_error = None

        if self.loaded:
            self._updateItems()

    @pyqtProperty(list, constant = True)
    def path(self):
        return self._path

    elementsChanged = pyqtSignal()

    @pyqtProperty(list, notify = elementsChanged)
    def elements(self):
        return self._items

    def _updateItems(self):
        from .DocumentsItem import DocumentsItem
        self._items = [DocumentsItem(child, self._api, self._path) for child in self._node.children]
        self.elementsChanged.emit()

        for item in self._items:
            item.selectedChanged.connect(self.selectedItemsChanged)

        self.selectedItemsChanged.emit()

    @pyqtProperty(bool, notify = elementsChanged)
    def loaded(self):
        return self._node.children_loaded

    @pyqtProperty(bool, constant = True)
    def isRoot(self):
        return isinstance(self._node.element, Root)

    errorChanged = pyqtSignal()

    @pyqtProperty(bool, notify = errorChanged)
    def hasError(self):
        return self._load_error is not None

    @pyqtProperty(str, notify = errorChanged)
    def error(self):
        return self._load_error

    @pyqtSlot()
    def load(self):
        def on_finished(children):
            self._node.setChildren(children)
            self._updateItems()

        def on_error(request, error):
            self._load_error = request.errorString()
            self.errorChanged.emit()

        for item in self._items:
            item.selected = False

        if not self.loaded:
            self._node.element.loadChildren(self._api, on_finished, on_error)

    @pyqtProperty(bool, constant = True)
    def refreshable(self):
        return self._node.element.is_refreshable

    @pyqtSlot()
    def refresh(self):
        self._items = []
        self._node.clear()

        self.elementsChanged.emit()

        self.load()

    selectedItemsChanged = pyqtSignal()

    @pyqtProperty(list, notify = selectedItemsChanged)
    def selectedItems(self):
        return [item for item in self._items if item.selected]
