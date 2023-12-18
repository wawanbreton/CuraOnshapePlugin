# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtProperty, pyqtSignal, QObject

from ..data.OnshapeRoot import OnshapeRoot


class OnshapeDocumentsModel(QObject):

    def __init__(self, node, api):
        super().__init__(parent = None)
        self._node = node
        self._api = api
        self._items = []

        if self.loaded:
            self._updateItems()

    @pyqtProperty(str, constant = True)
    def name(self):
        return self._node.element.name

    elementsChanged = pyqtSignal()

    @pyqtProperty(list, notify = elementsChanged)
    def elements(self):
        return self._items

    def setNodeChildren(self, children):
        self._node.setChildren(children)
        self._updateItems()

    def _updateItems(self):
        from .OnshapeDocumentsItem import OnshapeDocumentsItem
        self._items = [OnshapeDocumentsItem(child, self._api) for child in self._node.children]
        self.elementsChanged.emit()

    @pyqtProperty(bool, notify = elementsChanged)
    def loaded(self):
        return self._node.children_loaded

    @pyqtProperty(bool, constant = True)
    def isRoot(self):
        return isinstance(self._node.element, OnshapeRoot)
