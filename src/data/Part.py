# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any

from .BaseElement import BaseElement


class Part(BaseElement):
    """Represents a part that can be loaded to be buildplate"""

    def __init__(self, data: Dict[str, Any], document_id: str, workspace_id: str, tab_id: str):
        super().__init__(name = data['name'],
                         id = data['partId'],
                         thumbnail_url = self._findThumbnailUrl(data['thumbnailInfo']['sizes']),
                         has_children = False,
                         is_downloadable = True)
        self.document_id: str = document_id
        self.workspace_id: str = workspace_id
        self.tab_id: str = tab_id
