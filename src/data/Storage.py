# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Callable, List, Optional, TYPE_CHECKING

from UM.Qt.QtApplication import QtApplication

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply


class Storage(BaseElement):
    """Represents a storage place for the user, e.g. 'created by me' or 'shared with me' """

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data,
                         settable_as_default = True,
                         icon = QtApplication.getInstance().getTheme().getIcon('Folder', 'medium').toString() if QtApplication.getInstance().getTheme() is not None else None,
                         is_searchable = True)
        self._sub_type = data['subType']

    def _storeDefaultData(self, element_data: Dict[str, Any]):
        element_data['subType'] = self._sub_type

    def searchInside(self,
                     api: 'OnshapeApi',
                     search_query: str,
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:

        document_filter = 0
        if self._sub_type == 12: # Shared with me
            document_filter = 2
        elif self._sub_type == 12: # Created by me
            document_filter = 1

        api.search(search_query, on_finished, on_error, document_filter = document_filter, owner_id = self.id)
