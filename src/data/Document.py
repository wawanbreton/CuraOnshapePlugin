# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Callable, Optional, List, TYPE_CHECKING

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkReply
    from PyQt6.QtCore import QByteArray
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode


class Document(BaseElement):
    """Represents a document created by the user in his storage space"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data,
                         id = data['documentId'] if 'documentId' in data else None,
                         allow_single_child_shortcut = True,
                         has_thumbnail = True)

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.listWorkspaces(self.id, on_finished, on_error)

    def loadThumbnail(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[['QByteArray'], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.loadThumbnail(on_finished, on_error, document_id = self.id)
