# Copyright (c) 2023 Erwan MATHIEU

from .OnshapeElement import OnshapeBaseModel


class OnshapePart(OnshapeBaseModel):

    def __init__(self, data, document_id, workspace_id, tab_id):
        super().__init__(name = data['name'],
                         id = data['microversionId'],
                         thumbnail_url = self._findThumbnailUrl(data['thumbnailInfo']['sizes']),
                         has_children = False)
        self._document_id = document_id
        self._workspace_id = workspace_id
        self._tab_id = tab_id
