# Copyright (c) 2023 Erwan MATHIEU

import json

from PyQt6.QtCore import QObject, pyqtSlot, QUrlQuery, QUrl

from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.TaskManagement.HttpRequestScope import JsonDecoratorScope

from .OnshapeApiAuthScope import OnshapeApiAuthScope
from .OnshapeDocuments import OnshapeDocuments
from .AcceptBinaryDataScope import AcceptBinaryDataScope
from ..data.OnshapeWorkspace import OnshapeWorkspace
from ..data.OnshapeDocumentsTreeNode import OnshapeDocumentsTreeNode


class OnshapeApi(QObject):
    API_ROOT = 'https://cad.onshape.com/api/v6'
    DEFAULT_REQUEST_TIMEOUT = 10  # seconds
    QUERY_LIMIT = 20 # This is the default value of the API, make it explicit

    def __init__(self):
        super().__init__(parent = None)
        self._http = HttpRequestManager.getInstance()
        self._auth_scope = OnshapeApiAuthScope()
        self._json_scope = JsonDecoratorScope(self._auth_scope)
        self._binary_scope = AcceptBinaryDataScope(self._auth_scope)

    @pyqtSlot(str)
    def setToken(self, token):
        self._auth_scope.setToken(token)

    def _getFolders(self, on_finished, on_error, documents):
        def response_received(reply):
            data_json = json.loads(bytes(reply.readAll()).decode())
            documents.appendFolder(data_json)
            self._getFolders(on_finished, on_error, documents)

        next_folder = documents.getNextFolderToRetrieve()

        if next_folder is not None:
            url = f'{self.API_ROOT}/folders/{next_folder}'

            self._http.get(url,
                           scope = self._json_scope,
                           callback = response_received,
                           error_callback = on_error,
                           timeout = self.DEFAULT_REQUEST_TIMEOUT)
        else:
            on_finished(documents.getTree().children)

    def _listDocuments(self, on_finished, on_error, documents, offset):
        url = QUrl(f'{self.API_ROOT}/documents')

        query = QUrlQuery()
        query.addQueryItem('limit', str(self.QUERY_LIMIT))
        if offset > 0:
            query.addQueryItem('offset', str(offset))

        url.setQuery(query)

        def response_received(reply):
            data_json = json.loads(bytes(reply.readAll()).decode())
            documents.appendDocuments(data_json['items'])

            if data_json['next'] is not None:
                self._listDocuments(on_finished, on_error, documents, offset + self.QUERY_LIMIT)
            else:
                self._getFolders(on_finished, on_error, documents)

        self._http.get(url.toString(),
                       scope = self._json_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)

    def listDocuments(self, on_finished, on_error):
        documents = OnshapeDocuments()
        self._listDocuments(on_finished, on_error, documents, 0)

    def listWorkspaces(self, document_id, on_finished, on_error):
        def response_received(reply):
            data_json = json.loads(bytes(reply.readAll()).decode())
            workspaces = []

            for workspace_data in data_json:
                workspaces.append(OnshapeDocumentsTreeNode(OnshapeWorkspace(workspace_data)))

            on_finished(workspaces)

        url = f'{self.API_ROOT}/documents/d/{document_id}/workspaces'

        self._http.get(url,
                       scope = self._json_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)

    def loadThumbnail(self, thumbnail_url, on_finished, on_error):
        def response_received(reply):
            on_finished(reply.readAll())

        self._http.get(thumbnail_url,
                       scope = self._binary_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)
