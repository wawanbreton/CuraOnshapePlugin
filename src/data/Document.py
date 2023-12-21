# Copyright (c) 2023 Erwan MATHIEU

from .Element import Element


class Document(Element):

    def __init__(self, data):
        super().__init__(data,
                         thumbnail_url = self._findThumbnailUrl(data['thumbnail']['sizes']),
                         allow_single_child_shortcut = True)

    def _loadChildren(self, api, on_finished, on_error):
        api.listWorkspaces(self.id, on_finished, on_error)
