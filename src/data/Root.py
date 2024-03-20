# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Callable, List

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
        api.listDocuments(on_finished, on_error)
