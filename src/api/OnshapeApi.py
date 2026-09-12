# Copyright (c) 2023 Erwan MATHIEU

import json
import tempfile
import functools

from PyQt6.QtCore import QObject, pyqtSlot, QUrlQuery, QUrl

from typing import Callable, List, Dict, Optional, TYPE_CHECKING

from UM.Application import Application
from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.TaskManagement.HttpRequestScope import JsonDecoratorScope
from UM.Logger import Logger

from .ApiAuthScope import ApiAuthScope
from .AcceptBinaryDataScope import AcceptBinaryDataScope
from ..data.Folder import Folder
from ..data.Workspace import Workspace
from ..data.Tab import Tab
from ..data.Part import Part
from ..data.ResourceCompanyOwner import ResourceCompanyOwner
from ..data.ResourceUserOwner import ResourceUserOwner
from ..data.Storage import Storage
from ..data.Document import Document
from ..data.DocumentsTreeNode import DocumentsTreeNode

if TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply


class OnshapeApi(QObject):
    """Manager giving access to the required calls to the remote Onshape REST API"""

    API_ROOT = 'https://cad.onshape.com/api/v14' # Stay with version 14, version 17 gives a different result for /globaltreenodes
    DEFAULT_REQUEST_TIMEOUT = 20  # seconds
    DOWNLOAD_REQUEST_TIMEOUT = 60 # seconds
    THUMBNAIL_SIZE = '300x300'

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

    def _onResponseReceived(self,
                            reply: 'QNetworkReply',
                            on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                            request_body: Optional[str] = None,
                            **kwargs) -> None:
        """
        Internal convenience that parses any request response and builds the matching elements list

        :param reply The raw received reply that contains the request answer data
        :param on_finished Callback function called on success. Receives (children, url_load_next_page, request_body).
        :param request_body If the function was a POST request, this contains the body of the request that has been sent
        :param kwargs Extra arguments to be given when constructing some specific elements
        """

        data_json = bytes(reply.readAll()).decode()
        Logger.debug(str(data_json))
        data_json = json.loads(data_json)

        nodes = []

        # Find the proper sub-element where relevant items are stored, not always the same
        if 'items' in data_json:
            items = data_json['items']
        else:
            items = data_json

        elements = []
        for item in items:
            # Identify the type of element based on the item data
            if 'jsonType' in item:
                json_type = item['jsonType']

                if json_type == 'resource-owner':
                    resource_type = item['resourceType']
                    if resource_type == 'resourcecompanyowner':
                        elements.append(ResourceCompanyOwner(item))
                    elif resource_type == 'resourceuserowner':
                        elements.append(ResourceUserOwner(item))

                elif json_type == 'magic' and item['subType'] in [2, 12]: # Other types are not relevant
                    elements.append(Storage(item))

                elif json_type == 'folder':
                    elements.append(Folder(item))

                elif json_type == 'document-summary':
                    elements.append(Document(item))

                elif json_type == 'document-summary-search':
                    for search_hit in item['searchHits']:
                        type = search_hit['type']
                        Logger.debug(type)

                        if type == 'part':
                            elements.append(Part(search_hit))

                        elif type == 'element':
                            elements.append(Tab(search_hit))

                        elif type == 'folder':
                            elements.append(Folder(search_hit))

                        elif type == 'document':
                            elements.append(Document(search_hit))

            elif 'type' in item:
                type = item['type']

                if type == 'workspace':
                    elements.append(Workspace(item))

                elif type == 'Part Studio':
                    elements.append(Tab(item, **kwargs))

            elif 'partId' in item:
                elements.append(Part(item, **kwargs))

        for element in elements:
            nodes.append(DocumentsTreeNode(element))

        url_load_next_page = data_json['next'] if 'next' in data_json else None

        on_finished(nodes, url_load_next_page, request_body)

    def _call(self,
              url: QUrl,
              on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
              on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
              request_body: Optional[str] = None,
              **kwargs) -> None:
        """Internal convenience method to actually send a GET or POST request with the proper arguments"""

        if request_body is not None:
            Logger.debug(f"POST {url.toString()}")
            self._http.post(url.toString(),
                            data = request_body.encode("utf-8"),
                            scope = self._json_scope,
                            callback = functools.partial(self._onResponseReceived, on_finished = on_finished, request_body = request_body),
                            error_callback = on_error,
                            timeout = OnshapeApi.DEFAULT_REQUEST_TIMEOUT)
        else:
            Logger.debug(f"GET {url.toString()}")
            self._http.get(url.toString(),
                           scope = self._json_scope,
                           callback = functools.partial(self._onResponseReceived, on_finished = on_finished, **kwargs),
                           error_callback = on_error,
                           timeout = OnshapeApi.DEFAULT_REQUEST_TIMEOUT)


    def loadElements(self,
                     url: str,
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
                     request_body: Optional[str] = None) -> None:
        """Generic method to load a list of elements from a previously-retrieved URL"""

        self._call(QUrl(url), on_finished, on_error, request_body = request_body)

    def listStorages(self,
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available root storages"""

        self._call(QUrl(f'{self.API_ROOT}/globaltreenodes'), on_finished, on_error)

    def listDocuments(self,
                      folder_id: str,
                      on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available documents in the given folder"""

        self._call(QUrl(f'{self.API_ROOT}/globaltreenodes/folder/{folder_id}'), on_finished, on_error)

    def listWorkspaces(self,
                       document_id: str,
                       on_finished: Callable[[List['DocumentsTreeNode']], None],
                       on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available workspaces in the given document"""

        self._call(QUrl(f'{self.API_ROOT}/documents/d/{document_id}/workspaces'), on_finished, on_error)

    def listTabs(self,
                 document_id: str,
                 workspace_id: str,
                 on_finished: Callable[[List['DocumentsTreeNode']], None],
                 on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available tabs (sub-documents) in the given document"""

        url = QUrl(f'{self.API_ROOT}/documents/d/{document_id}/w/{workspace_id}/elements')

        query = QUrlQuery()
        query.addQueryItem('elementType', 'PARTSTUDIO') # We can only get parts from PartStudios
        url.setQuery(query)

        self._call(url, on_finished, on_error, document_id=document_id, workspace_id=workspace_id)

    def listParts(self,
                  document_id: str,
                  workspace_id: str,
                  tab_id: str,
                  on_finished: Callable[[List['DocumentsTreeNode']], None],
                  on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Lists the available parts in the given tab"""

        url = QUrl(f'{self.API_ROOT}/parts/d/{document_id}/w/{workspace_id}/e/{tab_id}')

        query = QUrlQuery()
        query.addQueryItem('includeFlatParts', 'false')
        url.setQuery(query)

        self._call(url, on_finished, on_error, document_id=document_id, workspace_id=workspace_id, tab_id=tab_id)

    def loadThumbnail(self,
                      on_finished: Callable[['QByteArray'], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
                      document_id: str,
                      workspace_id: Optional[str] = None,
                      tab_id: Optional[str] = None,
                      part_id: Optional[str] = None) -> None:
        """Loads the thumbnail image of an element"""
        def response_received(reply: 'QNetworkReply'):
            on_finished(reply.readAll())

        url = QUrl(f'{self.API_ROOT}/thumbnails/d/{document_id}{'/w/' + workspace_id if workspace_id is not None else ''}{'/e/' + tab_id if tab_id is not None else ''}{'/p/' + part_id if part_id is not None else ''}/s/{self.THUMBNAIL_SIZE}')

        self._http.get(url,
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

    def search(self,
               search_query: str,
               on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
               on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
               folder_id: Optional[str] = None,
               document_filter: int = 0,
               owner_id: Optional[str] = None) -> None:
        """
        Processes a textual search, given the current root path

        :param search_query The text to be looked for. Note that all non-alphanumeric characters will be filtered out to avoid injection.
        :param on_finished Callback function called on success. Receives (children, url_load_next_page, request_body).
        :param on_error Callback function called on communication error
        :param folder_id Optional folder ID argument to be inserted when looking inside a specific folder
        :param document_filter Optional document filter that indicates the origin of the expected results.
                               See https://cad.onshape.com/glassworks/explorer/#/Document/getDocuments
        :param owner_id When using a document_filter that requires an owner id, this specifies the ID of the owner in which to look for
        """

        url = QUrl(f'{self.API_ROOT}/documents/search')

        request_body = {}

        raw_query = []
        raw_query.append(f'_all:{''.join(char for char in search_query if char.isalnum())}')

        if folder_id is not None:
            raw_query.append(f'ancestorFolder:{folder_id}')

        if owner_id is not None:
            request_body["ownerId"] = owner_id

        request_body["rawQuery"] = ' '.join(raw_query)
        request_body["documentFilter"] = document_filter
        request_body["type"] = 'string'
        request_body = json.dumps(request_body)

        self._call(url, on_finished, on_error, request_body = request_body)
