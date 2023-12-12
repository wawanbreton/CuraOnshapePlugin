# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty


class OnshapeController(QObject):

    def __init__(self, auth_controller):
        super().__init__(parent = None)

        self._auth_controller = auth_controller
