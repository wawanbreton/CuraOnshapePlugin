# Copyright (c) 2023 Erwan MATHIEU

from .OnshapeBaseModel import OnshapeBaseModel


class OnshapeRoot(OnshapeBaseModel):

    def __init__(self):
        super().__init__('My documents', None)

    def loadChildren(self, api, on_finished, on_error):
        api.listDocuments(on_finished, on_error)
