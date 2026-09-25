# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, List, Dict, Tuple, Optional, Callable

import os
import math
import functools
import json

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty, QUrl

from cura.CuraApplication import CuraApplication
from cura.UI.PrintInformation import PrintInformation
from UM.Message import Message

from .model.DocumentsModel import DocumentsModel
from . import data as data_module
from .data.Root import Root
from .data.DocumentsTreeNode import DocumentsTreeNode
from .OnshapeObjectDecorator import OnshapeObjectDecorator

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
        self._temp_files: List[str] = []
        self._pending_parts: Dict[str, Dict] = {}
        self._original_reload_nodes: Optional[Callable] = None

        application = CuraApplication.getInstance()

        root_node = DocumentsTreeNode(Root())
        self._root_documents_model: DocumentsModel = DocumentsModel(root_node, self._api, [])
        self._default_documents_model: DocumentsModel = self._root_documents_model

        default_storage = application.getPreferences().getValue('plugin_onshape/default_storage')
        if default_storage != '':
            storage_data = json.loads(default_storage)
            default_storage_type = storage_data["type"]
            element_class = getattr(getattr(data_module, default_storage_type), default_storage_type)
            default_storage_node = DocumentsTreeNode(element_class(storage_data))
            self._default_documents_model = DocumentsModel(default_storage_node, self._api, [''])
            root_node.addChild(default_storage_node)
            root_node.children_loaded = False

        application.fileLoaded.connect(self._onFileLoaded)
        scene = application.getController().getScene()
        scene.sceneChanged.connect(self._onSceneChanged)
        self._hookScene(scene)

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
    def rootDocumentsModel(self) -> DocumentsModel:
        return self._root_documents_model

    @pyqtProperty(QObject, constant = True)
    def defaultDocumentsModel(self) -> DocumentsModel:
        return self._default_documents_model

    @pyqtSlot()
    def login(self) -> None:
        self._logged_in = False
        self.loggedInChanged.emit()

        self._root_documents_model.clear()
        if self._default_documents_model != self._root_documents_model:
            self._default_documents_model.clear()

        self._auth_controller.login()

    def _onFileLoaded(self, file_path: str) -> None:
        if file_path in self._temp_files:
            os.remove(file_path)
            self._temp_files.remove(file_path)

    def _onSceneChanged(self, *args) -> None:
        for changed_node in args:
            if changed_node.callDecoration("isSliceable"):
                actual_name = changed_node.getName()
                mesh_file = ""
                if changed_node.getMeshData() and changed_node.getMeshData().getFileName():
                    mesh_file = os.path.basename(changed_node.getMeshData().getFileName())

                matched_key = None
                if actual_name in self._pending_parts:
                    matched_key = actual_name
                elif mesh_file in self._pending_parts:
                    matched_key = mesh_file

                if matched_key:
                    metadata = self._pending_parts.pop(matched_key)
                    self._pending_parts.pop(actual_name, None)
                    self._pending_parts.pop(mesh_file, None)

                    changed_node.setName(metadata["part_name"])
                    changed_node.addDecorator(OnshapeObjectDecorator(
                        document_id = metadata["document_id"],
                        workspace_id = metadata["workspace_id"],
                        tab_id = metadata["tab_id"],
                        part_ids = metadata["part_ids"],
                        configuration = metadata["configuration"],
                        part_name = metadata["part_name"]
                    ))

    @staticmethod
    def _onMeshDownloadProgress(message: Message, transmitted: int, total: int) -> None:
        message.setProgress(math.floor(transmitted * 100.0 / total))

    def _onMeshDownloaded(self, message: Message, metadata: Dict, file_path: str):
        message.hide()

        # Save file name to delete the temp file once it has been loaded
        self._temp_files.append(file_path)

        # Save metadata to decorate the scene node once created
        base_name = os.path.basename(file_path)
        stem_name = os.path.splitext(base_name)[0]
        self._pending_parts[base_name] = metadata
        self._pending_parts[stem_name] = metadata

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
            part_ids = [element.id for element in elements]
            metadata = {
                "part_name": first_element.name,
                "document_id": first_element.document_id,
                "workspace_id": first_element.workspace_id,
                "tab_id": first_element.tab_id,
                "part_ids": part_ids,
                "configuration": first_element.configuration
            }

            self._api.downloadParts(first_element.document_id,
                                    first_element.workspace_id,
                                    first_element.tab_id,
                                    part_ids,
                                    first_element.configuration,
                                    functools.partial(OnshapeController._onMeshDownloadProgress, message),
                                    functools.partial(self._onMeshDownloaded, message, metadata),
                                    functools.partial(OnshapeController._onMeshDownloadError, message))

            print_information = CuraApplication.getInstance().getPrintInformation()
            if len(print_information.jobName) == 0 or print_information.jobName == PrintInformation.UNTITLED_JOB_NAME:
                print_information.setJobName(items_group[0].getPath()[-1], True)

        self.partSelected.emit()

    def _hookScene(self, scene) -> None:
        """Hooks into Scene.reloadNodes to intercept reloads of Onshape models."""
        original_reload_nodes = getattr(scene, "reloadNodes", None)
        if not callable(original_reload_nodes) or self._original_reload_nodes is not None:
            return

        self._original_reload_nodes = original_reload_nodes

        def custom_reload_nodes(nodes: List, file_path: str, on_done: Optional[Callable] = None) -> None:
            onshape_nodes: List[Tuple] = []
            regular_nodes: List = []

            for node in nodes:
                decorator = node.getDecorator(OnshapeObjectDecorator)
                if decorator is not None:
                    onshape_nodes.append((node, decorator))
                else:
                    regular_nodes.append(node)

            if regular_nodes:
                original_reload_nodes(regular_nodes, file_path, on_done)

            if onshape_nodes:
                self._reloadOnshapeNodes(original_reload_nodes, onshape_nodes, on_done)

        scene.reloadNodes = custom_reload_nodes

    def _reloadOnshapeNodes(self, original_reload_nodes: Callable, onshape_nodes: List[Tuple], on_done: Optional[Callable] = None) -> None:
        grouped: Dict[Tuple[str, str, str, Tuple[str, ...], Optional[str], str], List] = {}
        for node, decorator in onshape_nodes:
            key = (
                decorator.document_id,
                decorator.workspace_id,
                decorator.tab_id,
                tuple(decorator.part_ids),
                decorator.configuration,
                decorator.part_name
            )
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(node)

        for (doc_id, ws_id, tab_id, part_ids_tuple, config, part_name), target_nodes in grouped.items():
            message = Message(
                text = f"Reloading {part_name} from Onshape...",
                dismissable = False,
                lifetime = 0,
                progress = 0,
                title = "Reloading..."
            )
            message.setProgress(0)
            message.show()

            def on_download_finished(new_temp_file: str, msg: Message, nodes_to_reload: List) -> None:
                msg.hide()

                def cleanup(*args, **kwargs) -> None:
                    try:
                        if on_done:
                            on_done(*args, **kwargs)
                    finally:
                        if os.path.exists(new_temp_file):
                            os.remove(new_temp_file)

                original_reload_nodes(nodes_to_reload, new_temp_file, on_done = cleanup)

            self._api.downloadParts(
                doc_id,
                ws_id,
                tab_id,
                list(part_ids_tuple),
                config,
                functools.partial(OnshapeController._onMeshDownloadProgress, message),
                functools.partial(on_download_finished, msg = message, nodes_to_reload = target_nodes),
                functools.partial(OnshapeController._onMeshDownloadError, message)
            )
