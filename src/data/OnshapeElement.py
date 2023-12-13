# Copyright (c) 2023 Erwan MATHIEU

import re


class OnshapeElement:

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.parent_id = data['parentId']
