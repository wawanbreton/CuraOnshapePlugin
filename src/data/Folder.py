# Copyright (c) 2023 Erwan MATHIEU

from typing import Dict, Any

from UM.Qt.QtApplication import QtApplication

from .StorageElement import StorageElement


class Folder(StorageElement):
    """Represents a folder created by the user in his storage space"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data,
                         icon = QtApplication.getInstance().getTheme().getIcon('Folder', 'medium').toString())
