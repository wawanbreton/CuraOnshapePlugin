# Copyright (c) 2023 Erwan MATHIEU

from .OnshapeElement import OnshapeElement


class OnshapeDocument(OnshapeElement):

    def __init__(self, data):
        super().__init__(data,
                         thumbnail_url = self._findThumbnailUrl(data['thumbnail']['sizes']))

    def loadChildren(self, api, on_finished, on_error):
        api.listWorkspaces(self.id, on_finished, on_error)
