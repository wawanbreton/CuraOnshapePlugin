# Copyright (c) 2023 Erwan MATHIEU

import os
import math

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

    loggedInChanged = pyqtSignal()

    partSelected = pyqtSignal()

    def setLoggedIn(self, logged_in):
        self._logged_in = logged_in
        self.loggedInChanged.emit()

    @pyqtProperty(bool, notify = loggedInChanged, fset = setLoggedIn)
    def loggedIn(self):
        return self._logged_in

    @pyqtProperty(QAbstractItemModel, constant = True)
    def documentsModel(self):
        return self._documents_model

    @pyqtSlot()
    def login(self):
        self._auth_controller.login()

    def _onFileLoaded(self, file_path):
        os.remove(file_path)
        CuraApplication.getInstance().fileLoaded.disconnect(self._onFileLoaded)

    @pyqtSlot(DocumentsItem)
    def addToBuildPlate(self, item):
        message = Message(text = item.name,
                          dismissable = False,
                          lifetime = 0,
                          progress = 0,
                          title = "Downloading...")
        message.setProgress(0)
        message.show()

        def on_mesh_download_progress(transmitted, total):
            message.setProgress(math.floor(transmitted * 100.0 / total))

        def on_mesh_downloaded(file_path):
            message.hide()
            app = CuraApplication.getInstance()
            app.fileLoaded.connect(self._onFileLoaded)
            app.readLocalFile(QUrl.fromLocalFile(file_path), add_to_recent_files = False)

        def on_mesh_download_error(request, error):
            message.hide()
            error_message = Message(text = request.errorString(),
                                    title = "Request error",
                                    lifetime = 10,
                                    message_type = Message.MessageType.ERROR)
            error_message.show()

        item.downloadMesh(on_mesh_download_progress, on_mesh_downloaded, on_mesh_download_error)
        self.partSelected.emit()
