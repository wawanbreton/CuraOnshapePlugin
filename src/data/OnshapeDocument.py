# Copyright (c) 2023 Erwan MATHIEU

import re

from .OnshapeElement import OnshapeElement


class OnshapeDocument(OnshapeElement):

    regex_thumbnail_size = re.compile('^([0-9]+)x([0-9]+)$')

    def __init__(self, data):
        super().__init__(data)
        self.thumbnail_url = self._findThumbnailUrl(data['thumbnail']['sizes'])

    def _findThumbnailUrl(self, thumbnail_sizes):
        best_thumbnail = None
        biggest_size = 0

        for thumbnail in thumbnail_sizes:
            size_str = thumbnail['size']
            re_match = self.regex_thumbnail_size.match(size_str)
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
