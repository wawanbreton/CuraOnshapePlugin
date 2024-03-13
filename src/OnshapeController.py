# Copyright (c) 2023 Erwan MATHIEU

import os
import math
import functools

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty, QAbstractItemModel, QUrl

from cura.CuraApplication import CuraApplication
from UM.Logger import Logger
from UM.Message import Message

from .model.DocumentsModel import DocumentsModel
from .model.DocumentsItem import DocumentsItem
from .data.Root import Root
from .data.DocumentsTreeNode import DocumentsTreeNode


class OnshapeController(QObject):

    def __init__(self, auth_controller, api):
        super().__init__(parent = None)

        self._auth_controller = auth_controller
        self._api = api
        self._logged_in = False
        self._documents_model = DocumentsModel(DocumentsTreeNode(Root()), self._api, [])
        self._temp_files = []

        CuraApplication.getInstance().fileLoaded.connect(self._onFileLoaded)

    loggedInChanged = pyqtSignal()

    partSelected = pyqtSignal()

    def setLoggedIn(self, logged_in):
        if logged_in != self._logged_in:
            self._logged_in = logged_in
            self.loggedInChanged.emit()

    @pyqtProperty(bool, notify = loggedInChanged, fset = setLoggedIn)
    def loggedIn(self):
        return self._logged_in

    @pyqtProperty(QObject, constant = True)
    def documentsModel(self):
        return self._documents_model

    @pyqtSlot()
    def login(self):
        self._auth_controller.login()

    def _onFileLoaded(self, file_path):
        if file_path in self._temp_files:
            os.remove(file_path)
            self._temp_files.remove(file_path)
            print("File removed ", file_path)

    @staticmethod
    def _onMeshDownloadProgress(message, transmitted, total):
        message.setProgress(math.floor(transmitted * 100.0 / total))

    def _onMeshDownloaded(self, message, file_path):
        message.hide()
        self._temp_files.append(file_path)
        CuraApplication.getInstance().readLocalFile(QUrl.fromLocalFile(file_path), add_to_recent_files = False)

    @staticmethod
    def _onMeshDownloadError(message, request, error):
        message.hide()
        error_message = Message(text = request.errorString(),
                                title = "Request error",
                                lifetime = 10,
                                message_type = Message.MessageType.ERROR)
        error_message.show()

    @pyqtSlot(list, bool)
    def addToBuildPlate(self, items, grouped):
        if grouped:
            grouped_items = [items]
        else:
            grouped_items = [[item] for item in items]

        for items_group in grouped_items:
            message = Message(text = '\n'.join([item.name for item in items_group]),
                              dismissable = False,
                              lifetime = 0,
                              progress = 0,
                              title = "Downloading...")
            message.setProgress(0)
            message.show()

            elements = [item.element for item in items_group]

            first_element = elements[0]
            self._api.downloadParts(first_element.document_id,
                                    first_element.workspace_id,
                                    first_element.tab_id,
                                    [element.id for element in elements],
                                    functools.partial(OnshapeController._onMeshDownloadProgress, message),
                                    functools.partial(self._onMeshDownloaded, message),
                                    functools.partial(OnshapeController._onMeshDownloadError, message))

        self.partSelected.emit()
