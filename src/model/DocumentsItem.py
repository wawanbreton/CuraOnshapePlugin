# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal

from UM.Logger import Logger

from .DocumentsModel import DocumentsModel


class DocumentsItem(QObject):

    def __init__(self, node, api, path):
        super().__init__(parent = None)
        self._node = node
        self._api = api
        self.element = self._node.element
        self._subModel = DocumentsModel(self._node, self._api, path)
        self._thumbnail_str_data = None
        self._thumbnail_downloaded = False
        self._selected = False

    @pyqtProperty(str, constant = True)
    def name(self):
        return self.element.name

    iconChanged = pyqtSignal()

    def _onThumbnailReceived(self, data):
        self._thumbnail_str_data = "data:image/png;base64,"
        self._thumbnail_str_data += bytes(data.toBase64()).decode('utf-8')
        self.iconChanged.emit()

    def _onThumbnailError(self, request, error):
        Logger.warning(f'Error when retrieving thumbnail: {error}')

    @pyqtProperty(str, notify = iconChanged)
    def icon(self):
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
    def hasThumbnail(self):
        return self.element.hasThumbnail()

    @pyqtProperty(bool, constant = True)
    def hasChildren(self):
        return self.element.has_children

    @pyqtProperty(bool, constant = True)
    def isDownloadable(self):
        return self.element.is_downloadable

    @pyqtProperty(str, constant = True)
    def shortDesc(self):
        return self.element.short_desc

    @pyqtProperty(str, constant = True)
    def lastModifiedDate(self):
        if self.element.last_modified_date is not None:
            return self.element.last_modified_date.astimezone().strftime("%d-%m-%Y %H:%M")
        else:
            return None

    @pyqtProperty(str, constant = True)
    def lastModifiedBy(self):
        if self.element.last_modified_by is not None:
            return self.element.last_modified_by
        else:
            return None

    @pyqtProperty(DocumentsModel, constant = True)
    def childModel(self):
        return self._subModel

    selectedChanged = pyqtSignal()

    def setSelected(self, selected):
        self._selected = selected
        self.selectedChanged.emit()

    @pyqtProperty(bool, notify = selectedChanged, fset = setSelected)
    def selected(self):
        return self._selected
