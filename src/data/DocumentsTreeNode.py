# Copyright (c) 2023 Erwan MATHIEU

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .BaseElement import BaseElement


class DocumentsTreeNode:
    """
    Simple generic container to make a tree with the actual elements in the storage space. Each
    node always contains the actual element, and the children may be loaded later, sequentially
    or all at once. This way we can build the whole tree while the user navigates inside it.
    """

    def __init__(self, element: 'BaseElement'):
        self.element: 'BaseElement' = element
        self.children: List['DocumentsTreeNode'] = []
        self.children_loaded: bool = False

    def addChild(self, node: 'DocumentsTreeNode'):
        """Add a single child to the node, which can be called multiple times"""
        self.children.append(node)
        self.children_loaded = True

    def setChildren(self, nodes: List['DocumentsTreeNode']):
        """Adds all the children to the node at once, which is supposed to be called only once"""
        self.children = nodes
        self.children_loaded = True

    def getId(self):
        return self.element.id
