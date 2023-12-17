# Copyright (c) 2023 Erwan MATHIEU


class OnshapeDocumentsTreeNode:

    def __init__(self, element):
        self.element = element
        self.children = []
        self.children_loaded = False

    def addChild(self, element):
        self.children.append(element)
        self.children_loaded = True

    def setChildren(self, elements):
        self.children = elements
        self.children_loaded = True

    def getId(self):
        return self.element.id
