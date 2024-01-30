# Copyright (c) 2023 Erwan MATHIEU

from typing import List

from .BaseModel import BaseModel


class DocumentsTreeNode:

    def __init__(self, element):
        self.element: BaseModel = element
        self.children: List[DocumentsTreeNode] = []
        self.children_loaded: bool = False

    def addChild(self, node):
        self.children.append(node)
        self.children_loaded = True

    def setChildren(self, nodes):
        self.children = nodes
        self.children_loaded = True

    def getId(self):
        return self.element.id
