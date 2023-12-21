# Copyright (c) 2023 Erwan MATHIEU

import re

class BaseModel:

    regex_thumbnail_size = re.compile('^([0-9]+)x([0-9]+)$')

    def __init__(self,
                 name,
                 id,
                 short_desc = None,
                 last_modified_date = None,
                 last_modified_by = None,
                 thumbnail_url = None,
                 icon = None,
                 has_children = True,
                 is_downloadable = False,
                 allow_single_child_shortcut = False):
        self.name = name
        self.id = id
        self.short_desc = short_desc
        self.last_modified_date = last_modified_date
        self.last_modified_by = last_modified_by
        self.thumbnail_url = thumbnail_url
        self.icon = icon
        self.has_children = has_children
        self.is_downloadable = is_downloadable
        self._allow_single_child_shortcut = allow_single_child_shortcut

    def loadChildren(self, api, on_finished, on_error):
        def shortcut_callback(children):
            if len(children) == 1:
                children[0].element.loadChildren(api, on_finished, on_error)
            else:
                on_finished(children)

        self._loadChildren(api, shortcut_callback if self._allow_single_child_shortcut else on_finished, on_error)

    def _loadChildren(self, api, on_finished, on_error):
        return NotImplementedError(f'Children of {self.__class__} are not to be loaded')

    def downloadMesh(self, api, on_progress, on_finished, on_error):
        return NotImplementedError(f'Unable to download mesh for {self.__class__}')

    def hasThumbnail(self):
        return self.thumbnail_url is not None

    @staticmethod
    def _findThumbnailUrl(thumbnail_sizes):
        best_thumbnail = None
        biggest_size = 0

        for thumbnail in thumbnail_sizes:
            size_str = thumbnail['size']
            re_match = BaseModel.regex_thumbnail_size.match(size_str)
            if re_match is not None:
                width = int(re_match[1])
                height = int(re_match[2])
                if width == height and width > biggest_size:
                    biggest_size = width
                    best_thumbnail = thumbnail['href']

        if best_thumbnail is not None:
            return best_thumbnail
        elif len(thumbnail_sizes) > 0:
            return thumbnail_sizes[0]['href']
        else:
            return None
