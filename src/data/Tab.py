# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Callable, List

from .BaseElement import BaseElement


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
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]):
        api.listParts(self._document_id, self._workspace_id, self.id, on_finished, on_error)
