# Copyright (c) 2023 Erwan MATHIEU

from .BaseModel import BaseModel


class Part(BaseModel):

    def __init__(self, data, document_id, workspace_id, tab_id):
        super().__init__(name = data['name'],
                         id = data['partId'],
                         thumbnail_url = self._findThumbnailUrl(data['thumbnailInfo']['sizes']),
                         has_children = False,
                         is_downloadable = True)
        self._document_id = document_id
        self._workspace_id = workspace_id
        self._tab_id = tab_id

    def downloadMesh(self, api, on_progress, on_finished, on_error):
        api.downloadPart(self._document_id,
                         self._workspace_id,
                         self._tab_id,
                         self.id,
                         on_progress,
                         on_finished,
                         on_error)
