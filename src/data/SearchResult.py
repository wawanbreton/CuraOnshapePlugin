# Copyright (c) 2025 Erwan MATHIEU

from typing import TYPE_CHECKING, Callable, List, Optional

from UM.i18n import i18nCatalog

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply


class SearchResult(BaseElement):
    """Pseudo-element which represents all the elements returned by a search query"""

    def __init__(self, search_query: str, parent_element: BaseElement):
        super().__init__(data = None, name = i18nCatalog("onshape").i18nc("@label:text", "Search result"), is_searchable = True)
        self.search_query: str = search_query
        self._parent_element: BaseElement = parent_element

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        self._parent_element.searchInside(api, self.search_query, on_finished, on_error)
