# Copyright (c) 2023 Erwan MATHIEU


class OnshapeDocumentsTreeNode:

    def __init__(self, element):
        self.element = element
        self.children = []

    def addChild(self, element):
        self.children.append(element)

    def getId(self):
        return self.element.id if self.element is not None else None
