# Copyright (c) 2023 Erwan MATHIEU

from .OnshapeDocument import OnshapeDocument
from. OnshapeFolder import OnshapeFolder


class OnshapeDocuments:

    def __init__(self):
        self.documents = []
        self.folders = []

    def appendDocuments(self, documents_data):
        for document_data in documents_data:
            self.documents.append(OnshapeDocument(document_data))

    def appendFolder(self, folder_data):
        self.folders.append(OnshapeFolder(folder_data))

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
