# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, List, Dict

import os
import math
import functools

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty, QUrl

from cura.CuraApplication import CuraApplication
from cura.UI.PrintInformation import PrintInformation
from UM.Message import Message

from .model.DocumentsModel import DocumentsModel
from .data.Root import Root
from .data.DocumentsTreeNode import DocumentsTreeNode

if TYPE_CHECKING:
    from OAuthController import OAuthController
    from api.OnshapeApi import OnshapeApi
    from PyQt6.QtNetwork import QNetworkReply
    from model.DocumentsItem import DocumentsItem


class OnshapeController(QObject):
    """Main controller which exposes global actions to the UI"""

    def __init__(self, auth_controller: "OAuthController", api: "OnshapeApi"):
        super().__init__(parent = None)

        self._auth_controller: "OAuthController" = auth_controller
        self._api: "OnshapeApi" = api
        self._logged_in: bool = False
        self._documents_model: DocumentsModel = DocumentsModel(DocumentsTreeNode(Root()), self._api, [])
        self._temp_files: List[str] = []
        self._parts_names: Dict[str, str] = {}

        CuraApplication.getInstance().fileLoaded.connect(self._onFileLoaded)
        CuraApplication.getInstance().getController().getScene().sceneChanged.connect(self._onSceneChanged)

    loggedInChanged = pyqtSignal()

    partSelected = pyqtSignal()

    def setLoggedIn(self, logged_in: bool) -> None:
        if logged_in != self._logged_in:
            self._logged_in = logged_in
            self.loggedInChanged.emit()

    @pyqtProperty(bool, notify = loggedInChanged, fset = setLoggedIn)
    def loggedIn(self) -> bool:
        return self._logged_in

    @pyqtProperty(QObject, constant = True)
    def documentsModel(self) -> DocumentsModel:
        return self._documents_model

    @pyqtSlot()
    def login(self) -> None:
        self._logged_in = False
        self.loggedInChanged.emit()

        self._documents_model.clear()

        self._auth_controller.login()

    def _onFileLoaded(self, file_path: str) -> None:
        if file_path in self._temp_files:
            os.remove(file_path)
            self._temp_files.remove(file_path)
            print("File removed ", file_path)

    def _onSceneChanged(self, *args) -> None:
        for changed_node in args:
            if changed_node.callDecoration("isSliceable"):
                actual_name = changed_node.getName()
                if actual_name in self._parts_names:
                    changed_node.setName(self._parts_names[actual_name])
                    self._parts_names.remove(actual_name)

    @staticmethod
    def _onMeshDownloadProgress(message: Message, transmitted: int, total: int) -> None:
        message.setProgress(math.floor(transmitted * 100.0 / total))

    def _onMeshDownloaded(self, message: Message, part_name: str, file_path: str):
        message.hide()

        # Save file name to delete the temp file once it has been loaded
        self._temp_files.append(file_path)

        # Save part name to set it once the scene node has been created
        self._parts_names[os.path.basename(file_path)] = part_name

        CuraApplication.getInstance().readLocalFile(QUrl.fromLocalFile(file_path), add_to_recent_files = False)

    @staticmethod
    def _onMeshDownloadError(message: Message, request: 'QNetworkReply', error: 'QNetworkReply.NetworkError'):
        message.hide()
        error_message = Message(text = request.errorString(),
                                title = "Request error",
                                lifetime = 10,
                                message_type = Message.MessageType.ERROR)
        error_message.show()

    @pyqtSlot(list, bool)
    def addToBuildPlate(self, items: List["DocumentsItem"], grouped: bool):
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
                                    functools.partial(self._onMeshDownloaded, message, first_element.name),
                                    functools.partial(OnshapeController._onMeshDownloadError, message))

            print_information = CuraApplication.getInstance().getPrintInformation()
            if len(print_information.jobName) == 0 or print_information.jobName == PrintInformation.UNTITLED_JOB_NAME:
                print_information.setJobName(items_group[0].getPath()[-1], True)

        self.partSelected.emit()
