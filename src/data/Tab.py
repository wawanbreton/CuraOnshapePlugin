# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Dict, Any, Callable, List, Optional

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply


class Tab(BaseElement):
    """Represents a tab of a document"""

    def __init__(self, data: Dict[str, Any], document_id: str, workspace_id: str):
        super().__init__(name = data['name'],
                         id = data['id'],
                         thumbnail_url = self._findThumbnailUrl(data['thumbnailInfo']['sizes']))
        self._document_id: str = document_id
        self._workspace_id: str = workspace_id

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      configuration: Optional[str],
                      on_finished: Callable[[List['DocumentsTreeNode'], bool, int], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
                      offset: Optional[int] = None) -> None:
        api.listParts(self._document_id, self._workspace_id, self.id, configuration, lambda parts: on_finished(parts, False, 0), on_error)

    @property
    def supports_configuration(self) -> bool:
        return True

    def loadConfiguration(self,
                          api: 'OnshapeApi',
                          on_finished: Callable[[Dict[str, Any]], None],
                          on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.getConfiguration(self._document_id, self._workspace_id, self.id, on_finished, on_error)
