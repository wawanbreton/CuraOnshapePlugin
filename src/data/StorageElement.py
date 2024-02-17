# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any, Optional

from datetime import datetime

from .BaseElement import BaseElement


class StorageElement(BaseElement):
    """Base class for a storage element, folder or document"""

    def __init__(self,
                 data: Dict[str, Any],
                 thumbnail_url: Optional[str] = None,
                 icon: Optional[str] = None,
                 allow_single_child_shortcut: bool = False):
        super().__init__(data['name'],
                         data['id'],
                         data['owner']['name'],
                         datetime.fromisoformat(data['modifiedAt']),
                         data['modifiedBy']['name'],
                         thumbnail_url = thumbnail_url,
                         icon = icon,
                         allow_single_child_shortcut = allow_single_child_shortcut)

        self.parent_id: str = data['parentId']
