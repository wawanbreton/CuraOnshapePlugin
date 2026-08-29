# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Callable, List, Optional

from .BaseElement import BaseElement

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply


class Root(BaseElement):
    """Pseudo-element which represents the root of the storag space"""

    def __init__(self):
        super().__init__('', None)

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        def page_finished(children: List['DocumentsTreeNode'], has_more: bool, document_count: int):
            on_finished(children)

        api.listDocumentsPage(0, page_finished, on_error)

    def loadChildrenPage(self,
                         api: 'OnshapeApi',
                         offset: int,
                         on_finished: Callable[[List['DocumentsTreeNode'], bool, int], None],
                         on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Loads a single page of children starting at the given offset"""
        api.listDocumentsPage(offset, on_finished, on_error)
