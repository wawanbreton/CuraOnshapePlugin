# Copyright (c) 2023 Erwan MATHIEU

from .Document import Document
from .Folder import Folder
from .Root import Root
from .DocumentsTreeNode import DocumentsTreeNode


class Documents:

    def __init__(self):
        self.documents = []
        self.folders = []

    def appendDocuments(self, documents_data):
        for document_data in documents_data:
            self.documents.append(Document(document_data))

    def appendFolder(self, folder_data):
        self.folders.append(Folder(folder_data))

    def getNextFolderToRetrieve(self):
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
    def _findParent(node, parent_id):
        if node.getId() == parent_id:
            return node

        for child in node.children:
            parent = Documents._findParent(child, parent_id)
            if parent is not None:
                return parent

        return None

    def getTree(self):
        root = DocumentsTreeNode(Root())

        elements = self.folders + self.documents

        # Keep adding elements until we can't do any more
        added_element = True
        while added_element:
            added_element = False

            index = 0
            while index < len(elements):
                element = elements[index]
                parent = Documents._findParent(root, element.parent_id)

                if parent is not None:
                    parent.addChild(DocumentsTreeNode(element))
                    elements.pop(index)
                    index -= 1
                    added_element = True

                index += 1

        return root
