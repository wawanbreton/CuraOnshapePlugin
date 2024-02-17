# Copyright (c) 2023 Erwan MATHIEU

from typing import Callable, List, Dict, Any

from datetime import datetime
import os
import pathlib

from PyQt6.QtCore import QUrl

from .BaseElement import BaseElement


class Workspace(BaseElement):

    def __init__(self, data: Dict[str, Any]):
        dir = pathlib.Path(__file__).parent.resolve()
        icon_path = os.path.join(dir, '..', '..', 'resources', 'images', 'Workspace.svg')
        icon_url = QUrl.fromLocalFile(icon_path).toString()

        super().__init__(data['name'],
                         data['id'],
                         None,
                         datetime.fromisoformat(data['modifiedAt']),
                         data['lastModifier']['name'],
                         icon = icon_url,
                         allow_single_child_shortcut = True)

        self._document_id = data['documentId']

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode']], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]):
        api.listTabs(self._document_id, self.id, on_finished, on_error)
