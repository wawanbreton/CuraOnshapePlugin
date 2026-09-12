# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Dict, Any, Callable, List, Optional

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply


class Tab(BaseElement):
    """Represents a tab of a document"""

    def __init__(self, data: Dict[str, Any], document_id: Optional[str] = None, workspace_id: Optional[str] = None):
        super().__init__(data,
                         id = data['elementId'] if 'elementId' in data else None,
                         has_thumbnail = True)

        self._document_id: str = data['documentId'] if document_id is None else document_id
        self._workspace_id: str = data['versionOrWorkspaceId'] if workspace_id is None else workspace_id

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.listParts(self._document_id, self._workspace_id, self.id, on_finished, on_error)

    def loadThumbnail(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[['QByteArray'], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.loadThumbnail(on_finished, on_error, document_id = self._document_id, workspace_id = self._workspace_id, tab_id = self.id)