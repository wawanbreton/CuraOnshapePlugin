# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Dict, Any, Callable, List

from .StorageElement import StorageElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply

class Document(StorageElement):
    """Represents a document created by the user in his storage space"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data,
                         thumbnail_url = self._findThumbnailUrl(data['thumbnail']['sizes']),
                         allow_single_child_shortcut = True)

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.listWorkspaces(self.id, on_finished, on_error)
