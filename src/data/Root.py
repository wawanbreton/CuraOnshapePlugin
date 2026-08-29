# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Callable, List

from .BaseElement import BaseElement
from .UserStorage import UserStorage

if TYPE_CHECKING:
    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode
    from PyQt6.QtNetwork import QNetworkReply


class Root(BaseElement):
    """Pseudo-element which represents the root of the storag space"""

    def __init__(self):
        super().__init__('', None)
        self._storage: UserStorage = UserStorage()

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        def page_finished(children: List['DocumentsTreeNode'], has_more: bool, document_count: int):
            on_finished(children)

        api.listDocumentsPage(0, self._storage, page_finished, on_error)

    def loadChildrenPage(self,
                         api: 'OnshapeApi',
                         offset: int,
                         on_finished: Callable[[List['DocumentsTreeNode'], bool, int], None],
                         on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Loads a single page of children starting at the given offset"""
        api.listDocumentsPage(offset, self._storage, on_finished, on_error)

    def resetStorage(self) -> None:
        """Resets the shared storage, to be called when the document list is refreshed"""
        self._storage = UserStorage()
