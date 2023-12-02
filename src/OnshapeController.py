# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty

from .OAuthController import OAuthController


class OnshapeController(QObject):

    def __init__(self, application):
        super().__init__(parent = None)

        self._application = application
        self.auth_controller = OAuthController(self._application)
