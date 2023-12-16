# Copyright (c) 2023 Erwan MATHIEU

from datetime import datetime


class OnshapeElement:

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.owner = data['owner']['name']
        self.last_modified_date = datetime.fromisoformat(data['modifiedAt'])
        self.last_modified_by = data['modifiedBy']['name']
        self.parent_id = data['parentId']
