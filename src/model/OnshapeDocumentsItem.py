# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal

from UM.Qt.QtApplication import QtApplication
from UM.Logger import Logger

from ..data.OnshapeDocument import OnshapeDocument
from .OnshapeDocumentsModel import OnshapeDocumentsModel


class OnshapeDocumentsItem(QObject):

    def __init__(self, node, api):
        super().__init__(parent = None)
        self._node = node
        self._api = api
        self._element = self._node.element
        self._subModel = OnshapeDocumentsModel(self._node, self._api)
        self._thumbnail_str_data = None
        self._thumbnail_downloaded = False

    @pyqtProperty(str, constant = True)
    def name(self):
        return self._element.name

    iconChanged = pyqtSignal()

    def _onThumbnailReceived(self, data):
        self._thumbnail_str_data = "data:image/png;base64,"
        self._thumbnail_str_data += bytes(data.toBase64()).decode('utf-8')
        self.iconChanged.emit()

    def _onThumbnailError(self, request, error):
        Logger.warning(f'Error when retrieving thumbnail: {error}')

    @pyqtProperty(str, notify = iconChanged)
    def icon(self):
        if isinstance(self._element, OnshapeDocument):
            if self._thumbnail_str_data is not None:
                return self._thumbnail_str_data
            else:
                if not self._thumbnail_downloaded:
                    self._thumbnail_downloaded = True
                    if self._element.thumbnail_url is not None:
                        self._api.loadThumbnail(self._element.thumbnail_url,
                                                self._onThumbnailReceived,
                                                self._onThumbnailError)
                return None
        else:
            return QtApplication.getInstance().getTheme().getIcon('Folder', 'medium').toString()

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

    @pyqtProperty(OnshapeDocumentsModel, constant = True)
    def childModel(self):
        return self._subModel
