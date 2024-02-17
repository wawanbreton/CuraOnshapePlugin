# Copyright (c) 2023 Erwan MATHIEU

from typing import Callable, List

from UM.i18n import i18nCatalog

from .BaseElement import BaseElement


class Root(BaseElement):
    """Pseudo-element which represents the root of the storag space"""

    def __init__(self):
        super().__init__(i18nCatalog("onshape").i18nc("@label", "My documents"), None)

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]):
        api.listDocuments(on_finished, on_error)
