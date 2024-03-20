# Copyright (c) 2023 Erwan MATHIEU

import json
import tempfile

from PyQt6.QtCore import QObject, pyqtSlot, QUrlQuery, QUrl

from typing import Callable, List, TYPE_CHECKING

from UM.Application import Application
from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.TaskManagement.HttpRequestScope import JsonDecoratorScope

from .ApiAuthScope import ApiAuthScope
from .AcceptBinaryDataScope import AcceptBinaryDataScope
from ..data.UserStorage import UserStorage
from ..data.Workspace import Workspace
from ..data.Tab import Tab
from ..data.Part import Part
from ..data.DocumentsTreeNode import DocumentsTreeNode

if TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply


class OnshapeApi(QObject):
    """Manager giving access to the required calls to the remote Onshape REST API"""

    API_ROOT = 'https://cad.onshape.com/api/v6'
    DEFAULT_REQUEST_TIMEOUT = 10  # seconds
    DOWNLOAD_REQUEST_TIMEOUT = 60 # seconds
    QUERY_LIMIT = 20 # This is the default value of the API, make it explicit

    def __init__(self):
        super().__init__()
        self._http: 'HttpRequestManager' = HttpRequestManager.getInstance()
        self._auth_scope: 'ApiAuthScope' = ApiAuthScope()
        self._json_scope: 'JsonDecoratorScope' = JsonDecoratorScope(self._auth_scope)
        self._binary_scope: 'AcceptBinaryDataScope' = AcceptBinaryDataScope(self._auth_scope)

    @pyqtSlot(str)
    def setToken(self, token: str) -> None:
        """Sets the authentication token, which is required to make API calls"""
        self._auth_scope.setToken(token)

    def _getFolders(self,
                    on_finished: Callable[[List['DocumentsTreeNode']], None],
                    on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
                    storage: 'UserStorage') -> None:
        """
        Retrieves the next required folder content, which is done recursively and dynamically
        because we don't know in advance which subfolders are existing and non-empty.
        """

        def response_received(reply: 'QNetworkReply'):
            data_json = json.loads(bytes(reply.readAll()).decode())
            storage.appendFolder(data_json)
            self._getFolders(on_finished, on_error, storage)

        next_folder = storage.getNextFolderToRetrieve()

        if next_folder is not None:
            url = f'{self.API_ROOT}/folders/{next_folder}'

            self._http.get(url,
                           scope = self._json_scope,
                           callback = response_received,
                           error_callback = on_error,
                           timeout = self.DEFAULT_REQUEST_TIMEOUT)
        else:
            on_finished(storage.getTree().children)

    def _listDocuments(self,
                       on_finished: Callable[[List['DocumentsTreeNode']], None],
                       on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
                       storage: 'UserStorage',
                       offset: int) -> None:
        """
        Retrieves the list of root documents in the user storage. This is done multiple times
        because each call retrieves a sublist of the total, hence the given offset. Once the
        documents are complete, we also start receiving the folders tree.
        """

        url = QUrl(f'{self.API_ROOT}/documents')

        query = QUrlQuery()
        query.addQueryItem('limit', str(self.QUERY_LIMIT))
        if offset > 0:
            query.addQueryItem('offset', str(offset))

        url.setQuery(query)

        def response_received(reply: 'QNetworkReply'):
            data_json = json.loads(bytes(reply.readAll()).decode())
            storage.appendDocuments(data_json['items'])

            if data_json['next'] is not None:
                self._listDocuments(on_finished, on_error, storage, offset + self.QUERY_LIMIT)
            else:
                self._getFolders(on_finished, on_error, storage)

        self._http.get(url.toString(),
                       scope = self._json_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)

    def listDocuments(self,
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the root documents and the whole folder tree present in the user storage"""
        storage = UserStorage()
        self._listDocuments(on_finished, on_error, storage, 0)

    def listWorkspaces(self,
                       document_id: str,
                       on_finished: Callable[[List['DocumentsTreeNode']], None],
                       on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available workspaces in the given document"""
        def response_received(reply: 'QNetworkReply'):
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

    def listTabs(self,
                 document_id: str,
                 workspace_id: str,
                 on_finished: Callable[[List['DocumentsTreeNode']], None],
                 on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available tabs (sub-documents) in the given document"""
        def response_received(reply: 'QNetworkReply'):
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

    def listParts(self,
                  document_id: str,
                  workspace_id: str,
                  tab_id: str,
                  on_finished: Callable[[List['DocumentsTreeNode']], None],
                  on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available parts in the given tab"""
        def response_received(reply: 'QNetworkReply'):
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

    def loadThumbnail(self,
                      thumbnail_url: str,
                      on_finished: Callable[['QByteArray'], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Loads the thumbnail image, to be found at the given URL"""
        def response_received(reply: 'QNetworkReply'):
            on_finished(reply.readAll())

        self._http.get(thumbnail_url,
                       scope = self._binary_scope,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)

    def downloadParts(self,
                      document_id: str,
                      workspace_id: str,
                      tab_id: str,
                      parts_ids: List[str],
                      on_progress: Callable[[int, int], None],
                      on_finished: Callable[[str], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """
        Downloads the given part(s) as STL data into a local file.
        The finished callback receives the path of the created local file.
        The created file will be placed in a temporary folder. However, it is up to the caller to
        remove the file as soon as it is no more required.
        """
        def response_received(reply: 'QNetworkReply'):
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.stl', delete=False) as file:
                file.write(reply.readAll())
                on_finished(file.name)

        url = QUrl(f'{self.API_ROOT}/partstudios/d/{document_id}/w/{workspace_id}/e/{tab_id}/stl')

        query = QUrlQuery()
        query.addQueryItem('partIds', ','.join(parts_ids))
        query.addQueryItem('units', 'millimeter')
        query.addQueryItem('mode', 'binary')

        resolution = Application.getInstance().getPreferences().getValue('plugin_onshape/tesselation_resolution')
        if resolution == 'coarse':
            precision = '0.04'
        elif resolution == 'fine':
            precision = '0.01'
        else:
            precision = '0.02'

        query.addQueryItem('angleTolerance', precision)
        query.addQueryItem('chordTolerance', precision)

        query.addQueryItem('grouping', 'true')
        url.setQuery(query)

        self._http.get(url,
                       scope = self._binary_scope,
                       download_progress_callback = on_progress,
                       callback = response_received,
                       error_callback = on_error,
                       timeout = self.DOWNLOAD_REQUEST_TIMEOUT)
