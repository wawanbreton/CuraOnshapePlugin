# Copyright (c) 2023 Erwan MATHIEU

from UM.Qt.QtApplication import QtApplication

from .Element import Element


class Folder(Element):

    def __init__(self, data):
        super().__init__(data,
                         icon = QtApplication.getInstance().getTheme().getIcon('Folder', 'medium').toString())
