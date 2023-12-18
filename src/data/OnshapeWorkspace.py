# Copyright (c) 2023 Erwan MATHIEU

from datetime import datetime
import os
import pathlib

from PyQt6.QtCore import QUrl

from .OnshapeElement import OnshapeBaseModel


class OnshapeWorkspace(OnshapeBaseModel):

    def __init__(self, data):
        super().__init__(data['name'], data['id'])

        self.last_modified_date = datetime.fromisoformat(data['modifiedAt'])
        self.last_modified_by = data['lastModifier']['name']

    def getIcon(self):
        dir = pathlib.Path(__file__).parent.resolve()
        icon_path = os.path.join(dir, '..', '..', 'resources', 'images', 'Workspace.svg')
        return QUrl.fromLocalFile(icon_path).toString()
