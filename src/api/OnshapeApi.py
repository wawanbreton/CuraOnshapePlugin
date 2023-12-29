# Copyright (c) 2023 Erwan MATHIEU

import json
import tempfile

from PyQt6.QtCore import QObject, pyqtSlot, QUrlQuery, QUrl

from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.TaskManagement.HttpRequestScope import JsonDecoratorScope

from .ApiAuthScope import ApiAuthScope
from .AcceptBinaryDataScope import AcceptBinaryDataScope
from ..data.Documents import Documents
from ..data.Workspace import Workspace
from ..data.Tab import Tab
from ..data.Part import Part
from ..data.DocumentsTreeNode import DocumentsTreeNode


class OnshapeApi(QObject):
    API_ROOT = 'https://cad.onshape.com/api/v6'
    DEFAULT_REQUEST_TIMEOUT = 10  # seconds
    DOWNLOAD_REQUEST_TIMEOUT = 60 # seconds
    QUERY_LIMIT = 20 # This is the default value of the API, make it explicit

    def __init__(self):
        super().__init__(parent = None)
        self._http = HttpRequestManager.getInstance()
        self._auth_scope = ApiAuthScope()
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
        documents = Documents()
        self._listDocuments(on_finished, on_error, documents, 0)

    def listWorkspaces(self, document_id, on_finished, on_error):
        def response_received(reply):
            data_json = json.loads(bytes(reply.readAll()).decode())
            workspaces = []

            for workspace_data in data_json:
                workspaces.append(DocumentsTreeNode(Workspace(workspace_data)))

            on_finished(workspaces)

        url = f'{self.API_ROOT}/documents/d/{document_id}/workspaces'

        self._http.get(url,
                       scope = self._json_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)

    def listTabs(self, document_id, workspace_id, on_finished, on_error):
        def response_received(reply):
            tabs = []
            data_json = json.loads(bytes(reply.readAll()).decode())

            for tab_data in data_json:
                tabs.append(DocumentsTreeNode(Tab(tab_data, document_id, workspace_id)))

            on_finished(tabs)

        url = QUrl(f'{self.API_ROOT}/documents/d/{document_id}/w/{workspace_id}/elements')

        query = QUrlQuery()
        query.addQueryItem('withThumbnails', 'true')
        query.addQueryItem('elementType', 'PARTSTUDIO') # We can only get parts from PartStudios
        url.setQuery(query)

        self._http.get(url,
                       scope = self._json_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)

    def listParts(self, document_id, workspace_id, tab_id, on_finished, on_error):
        def response_received(reply):
            parts = []
            data_json = json.loads(bytes(reply.readAll()).decode())

            for part_data in data_json:
                parts.append(DocumentsTreeNode(Part(part_data, document_id, workspace_id, tab_id)))

            on_finished(parts)

        url = QUrl(f'{self.API_ROOT}/parts/d/{document_id}/w/{workspace_id}/e/{tab_id}')

        query = QUrlQuery()
        query.addQueryItem('withThumbnails', 'true')
        query.addQueryItem('includeFlatParts', 'false')
        url.setQuery(query)

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

    def downloadParts(self, document_id, workspace_id, tab_id, parts_ids, on_progress, on_finished, on_error):
        def response_received(reply):
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.stl', delete=False) as file:
                file.write(reply.readAll())
                on_finished(file.name)

        url = QUrl(f'{self.API_ROOT}/partstudios/d/{document_id}/w/{workspace_id}/e/{tab_id}/stl')

        query = QUrlQuery()
        query.addQueryItem('partIds', ','.join(parts_ids))
        query.addQueryItem('units', 'millimeter')
        query.addQueryItem('mode', 'binary')
        query.addQueryItem('angleTolerance', '0.01')
        query.addQueryItem('chordTolerance', '0.01')
        query.addQueryItem('grouping', 'true')
        url.setQuery(query)

        self._http.get(url,
                       scope = self._binary_scope,
                       download_progress_callback = on_progress,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DOWNLOAD_REQUEST_TIMEOUT)
