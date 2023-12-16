# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtProperty, pyqtSignal, QObject

from .OnshapeDocumentsItem import OnshapeDocumentsItem


class OnshapeDocumentsModel(QObject):

    def __init__(self, node):
        super().__init__(parent = None)
        self._node = node

        self._items = [OnshapeDocumentsItem(child) for child in self._node.children]

    elementsChanged = pyqtSignal()

    @pyqtProperty(list, notify = elementsChanged)
    def elements(self):
        return self._items
