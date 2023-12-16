# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import Qt, QAbstractListModel, pyqtSlot, QVariant

from UM.Qt.QtApplication import QtApplication

from .OnshapeDocument import OnshapeDocument


class OnshapeDocumentsModel(QAbstractListModel):
    HasThumbnailRole = Qt.ItemDataRole.UserRole + 1
    OwnerRole = Qt.ItemDataRole.UserRole + 2
    LastModifiedDate = Qt.ItemDataRole.UserRole + 3
    LastModifiedBy = Qt.ItemDataRole.UserRole + 4

    def __init__(self, node):
        super().__init__(parent = None)
        self._node = node

    def roleNames(self):
        return { Qt.ItemDataRole.DisplayRole: 'name'.encode("utf-8"),
                 Qt.ItemDataRole.DecorationRole: 'icon'.encode("utf-8"),
                 self.HasThumbnailRole: 'hasThumbnail'.encode("utf-8"),
                 self.OwnerRole: 'owner'.encode("utf-8"),
                 self.LastModifiedDate: 'lastModifiedDate'.encode("utf-8"),
                 self.LastModifiedBy: 'lastModifiedBy'.encode("utf-8") }

    @pyqtSlot(result = int)
    def rowCount(self, parent = None):
        return len(self._node.children)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        child = self._node.children[index.row()].element

        if role == Qt.ItemDataRole.DisplayRole:
            return child.name
        elif role == self.HasThumbnailRole:
            return isinstance(child, OnshapeDocument)
        elif role == Qt.ItemDataRole.DecorationRole:
            if isinstance(child, OnshapeDocument):
                return child.thumbnail_url
            else:
                return QtApplication.getInstance().getTheme().getIcon('Folder')
        elif role == self.OwnerRole:
            return child.owner
        elif role == self.LastModifiedDate:
            return child.last_modified_date.astimezone().strftime("%d-%m-%Y %H:%M")
        elif role == self.LastModifiedBy:
            return child.last_modified_by

