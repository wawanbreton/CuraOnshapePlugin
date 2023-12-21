# Copyright (c) 2023 Erwan MATHIEU

from datetime import datetime

from .BaseModel import BaseModel


class Element(BaseModel):

    def __init__(self, data, thumbnail_url = None, icon = None):
        super().__init__(data['name'],
                         data['id'],
                         data['owner']['name'],
                         datetime.fromisoformat(data['modifiedAt']),
                         data['modifiedBy']['name'],
                         thumbnail_url = thumbnail_url,
                         icon = icon)

        self.parent_id = data['parentId']
