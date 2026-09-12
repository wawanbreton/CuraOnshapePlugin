# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Optional, Callable, List, TYPE_CHECKING

from UM.Qt.QtApplication import QtApplication

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from PyQt6.QtNetwork import QNetworkReply
    from .DocumentsTreeNode import DocumentsTreeNode


class Folder(BaseElement):
    """Represents a folder created by the user in his storage space"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data,
                         id = data['folderId'] if 'folderId' in data else None,
                         icon = QtApplication.getInstance().getTheme().getIcon('Folder', 'medium').toString(),
                         is_searchable = True)

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]):
        api.listDocuments(self.id, on_finished, on_error)

    def searchInside(self,
                     api: 'OnshapeApi',
                     search_query: str,
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.search(search_query, on_finished, on_error, folder_id = self.id)
