# Copyright (c) 2023 Erwan MATHIEU


class OnshapeDocumentsTreeNode:

    def __init__(self, element):
        self.element = element
        self.children = []
        self.children_loaded = False

    def addChild(self, node):
        self.children.append(node)
        self.children_loaded = True

    def setChildren(self, nodes):
        self.children = nodes
        self.children_loaded = True

    def getId(self):
        return self.element.id
