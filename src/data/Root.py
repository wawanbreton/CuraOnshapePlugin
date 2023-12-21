# Copyright (c) 2023 Erwan MATHIEU

from .BaseModel import BaseModel


class Root(BaseModel):

    def __init__(self):
        super().__init__('My documents', None)

    def _loadChildren(self, api, on_finished, on_error):
        api.listDocuments(on_finished, on_error)
