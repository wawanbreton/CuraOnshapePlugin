# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Callable, List, Optional

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
                      on_finished: Callable[[List['DocumentsTreeNode'], bool, int], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None],
                      offset: Optional[int] = None) -> None:
        api.listDocuments(0 if offset is None else offset, self._storage, on_finished, on_error)

    def resetStorage(self) -> None:
        """Resets the shared storage, to be called when the document list is refreshed"""
        self._storage = UserStorage()
