# Copyright (c) 2024 Erwan MATHIEU

from typing import List, Optional, Dict
from UM.Scene.SceneNodeDecorator import SceneNodeDecorator


class OnshapeObjectDecorator(SceneNodeDecorator):
    """
    Decorator attached to SceneNodes loaded from Onshape to store
    document/part metadata for reloading or updating models.
    """

    def __init__(self,
                 document_id: str,
                 workspace_id: str,
                 tab_id: str,
                 part_ids: List[str],
                 configuration: Optional[str] = None,
                 part_name: str = "") -> None:
        super().__init__()
        self.document_id: str = document_id
        self.workspace_id: str = workspace_id
        self.tab_id: str = tab_id
        self.part_ids: List[str] = part_ids
        self.configuration: Optional[str] = configuration
        self.part_name: str = part_name

    def isOnshapeObject(self) -> bool:
        return True

    def getOnshapeMetadata(self) -> Dict:
        return {
            "document_id": self.document_id,
            "workspace_id": self.workspace_id,
            "tab_id": self.tab_id,
            "part_ids": self.part_ids,
            "configuration": self.configuration,
            "part_name": self.part_name
        }

    def __deepcopy__(self, memo: Dict[int, object]) -> "OnshapeObjectDecorator":
        return OnshapeObjectDecorator(
            self.document_id,
            self.workspace_id,
            self.tab_id,
            list(self.part_ids),
            self.configuration,
            self.part_name
        )
