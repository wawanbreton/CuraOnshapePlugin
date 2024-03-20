# Copyright (c) 2023 Erwan MATHIEU

from typing import List, Optional, Dict, Any

from .Document import Document
from .Folder import Folder
from .Root import Root
from .DocumentsTreeNode import DocumentsTreeNode


class UserStorage:
    """
    Represents a view of the user storage, containing folders and documents. This view is to be
    completed with multiple requests, as we can't load all the folders at once and we also don't
    known which subfolders are useful.
    """

    def __init__(self):
        self.documents: List[Document] = []
        self.folders: List[Folder] = []

    def appendDocuments(self, documents_data: List[Dict[str, Any]]) -> None:
        for document_data in documents_data:
            self.documents.append(Document(document_data))

    def appendFolder(self, folder_data: Dict[str, Any]) -> None:
        self.folders.append(Folder(folder_data))

    def getNextFolderToRetrieve(self) -> Optional[Folder]:
        folders = set()

        for element in self.documents + self.folders:
            if element.parent_id is not None:
                folders.add(element.parent_id)

        for folder in self.folders:
            if folder.id in folders:
                folders.remove(folder.id)

        if len(folders) > 0:
            return folders.pop()
        else:
            return None

    @staticmethod
    def _findParent(node: DocumentsTreeNode, parent_id: str) -> Optional[DocumentsTreeNode]:
        if node.getId() == parent_id:
            return node

        for child in node.children:
            parent = UserStorage._findParent(child, parent_id)
            if parent is not None:
                return parent

        return None

    def getTree(self) -> DocumentsTreeNode:
        root = DocumentsTreeNode(Root())

        elements = self.folders + self.documents

        # Keep adding elements until we can't do any more
        added_element = True
        while added_element:
            added_element = False

            index = 0
            while index < len(elements):
                element = elements[index]
                parent = UserStorage._findParent(root, element.parent_id)

                if parent is not None:
                    parent.addChild(DocumentsTreeNode(element))
                    elements.pop(index)
                    index -= 1
                    added_element = True

                index += 1

        return root
