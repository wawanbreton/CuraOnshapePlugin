# Copyright (c) 2023 Erwan MATHIEU

from datetime import datetime

from .OnshapeBaseModel import OnshapeBaseModel


class OnshapeElement(OnshapeBaseModel):

    def __init__(self, data):
        super().__init__(data['name'], data['id'])

        self.owner = data['owner']['name']
        self.last_modified_date = datetime.fromisoformat(data['modifiedAt'])
        self.last_modified_by = data['modifiedBy']['name']
        self.parent_id = data['parentId']
