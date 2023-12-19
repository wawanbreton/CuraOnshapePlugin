# Copyright (c) 2023 Erwan MATHIEU

from UM.Qt.QtApplication import QtApplication

from .OnshapeElement import OnshapeElement


class OnshapeFolder(OnshapeElement):

    def __init__(self, data):
        super().__init__(data,
                         icon = QtApplication.getInstance().getTheme().getIcon('Folder', 'medium').toString())
