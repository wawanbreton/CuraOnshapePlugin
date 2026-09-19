# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Callable, List, Optional, TYPE_CHECKING

from UM.Qt.QtApplication import QtApplication

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply


class ResourceCompanyOwner(BaseElement):
    """Represents a company-owned storage in the user storage space"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data,
                         settable_as_default = True,
                         icon = QtApplication.getInstance().getTheme().getIcon('Shop', 'default').toString() if QtApplication.getInstance().getTheme() is not None else None,
                         is_searchable = True)

    def searchInside(self,
                     api: 'OnshapeApi',
                     search_query: str,
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        api.search(search_query, on_finished, on_error, document_filter = 7, owner_id = self.id)