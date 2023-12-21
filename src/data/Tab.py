# Copyright (c) 2023 Erwan MATHIEU

from .Element import BaseModel


class Tab(BaseModel):

    def __init__(self, data, document_id, workspace_id):
        super().__init__(name = data['name'],
                         id = data['id'],
                         thumbnail_url = self._findThumbnailUrl(data['thumbnailInfo']['sizes']))
        self._document_id = document_id
        self._workspace_id = workspace_id

    def loadChildren(self, api, on_finished, on_error):
        api.listParts(self._document_id, self._workspace_id, self.id, on_finished, on_error)
