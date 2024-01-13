# Copyright (c) 2023 Erwan MATHIEU

from UM.i18n import i18nCatalog

from .BaseModel import BaseModel


class Root(BaseModel):

    def __init__(self):
        super().__init__(i18nCatalog("onshape").i18nc("@label", "My documents"), None)

    def _loadChildren(self, api, on_finished, on_error):
        api.listDocuments(on_finished, on_error)
