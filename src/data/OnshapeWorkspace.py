# Copyright (c) 2023 Erwan MATHIEU

from datetime import datetime
import os
import pathlib

from PyQt6.QtCore import QUrl

from .OnshapeElement import OnshapeBaseModel


class OnshapeWorkspace(OnshapeBaseModel):

    def __init__(self, data):
        dir = pathlib.Path(__file__).parent.resolve()
        icon_path = os.path.join(dir, '..', '..', 'resources', 'images', 'Workspace.svg')
        icon_url = QUrl.fromLocalFile(icon_path).toString()

        super().__init__(data['name'],
                         data['id'],
                         None,
                         datetime.fromisoformat(data['modifiedAt']),
                         data['lastModifier']['name'],
                         icon = icon_url)

        self._document_id = data['documentId']

    def loadChildren(self, api, on_finished, on_error):
        api.listTabs(self._document_id, self.id, on_finished, on_error)
