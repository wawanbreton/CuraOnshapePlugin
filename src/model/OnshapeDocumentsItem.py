# Copyright (c) 2023 Erwan MATHIEU

from UM.Qt.QtApplication import QtApplication

from PyQt6.QtCore import pyqtProperty, QObject
from PyQt6.QtQml import QQmlEngine

from ..data.OnshapeDocument import OnshapeDocument


class OnshapeDocumentsItem(QObject):

    def __init__(self, node):
        super().__init__(parent = None)
        QQmlEngine.setObjectOwnership(self, QQmlEngine.ObjectOwnership.CppOwnership)
        self._node = node
        self._element = self._node.element

    @pyqtProperty(str, constant = True)
    def name(self):
        return self._element.name

    @pyqtProperty(str, constant=True)
    def icon(self):
        if isinstance(self._element, OnshapeDocument):
            return self._element.thumbnail_url
        else:
            return QtApplication.getInstance().getTheme().getIcon('Folder').toString()

    @pyqtProperty(bool, constant = True)
    def hasThumbnail(self):
        return isinstance(self._element, OnshapeDocument)

    @pyqtProperty(str, constant = True)
    def owner(self):
        return self._element.owner

    @pyqtProperty(str, constant = True)
    def lastModifiedDate(self):
        return self._element.last_modified_date.astimezone().strftime("%d-%m-%Y %H:%M")

    @pyqtProperty(str, constant = True)
    def lastModifiedBy(self):
        return self._element.last_modified_by
