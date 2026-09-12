# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Optional, Callable, TYPE_CHECKING

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply


class Part(BaseElement):
    """Represents a part that can be loaded to be buildplate"""

    def __init__(self,
                 data: Dict[str, Any],
                 document_id: Optional[str] = None,
                 workspace_id: Optional[str] = None,
                 tab_id: Optional[str] = None):
        super().__init__(data, id = data['partId'], has_children = False, is_downloadable = True, has_thumbnail = True)

        self.document_id: str = data['documentId'] if document_id is None else document_id
        self.workspace_id: str = data['versionOrWorkspaceId'] if workspace_id is None else workspace_id
        self.tab_id: str = data['elementId'] if tab_id is None else tab_id

    def loadThumbnail(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[['QByteArray'], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.loadThumbnail(on_finished,
                          on_error,
                          document_id = self.document_id,
                          workspace_id = self.workspace_id,
                          tab_id = self.tab_id,
                          part_id = self.id)
