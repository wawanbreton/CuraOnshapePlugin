# Copyright (c) 2023 Erwan MATHIEU

import os

from PyQt6.QtCore import pyqtSlot

from UM.FileProvider import FileProvider

from .OnshapeController import OnshapeController
from .OAuthController import OAuthController
from .OnshapeApi import OnshapeApi


class OnshapeFileProvider(FileProvider):

    def __init__(self, application):
        super().__init__()
        self.menu_item_display_text = 'From Onshape'
        self.shortcut = 'Ctrl+Alt+O'
        self._application = application
        self._auth_controller = OAuthController(self._application)
        self._api = OnshapeApi()
        self._controller = OnshapeController(self._auth_controller, self._api)

        self._auth_controller.tokenChanged.connect(self._api.setToken)
        self._auth_controller.tokenChanged.connect(self._onTokenChanged)

    def run(self):
        plugin_path = os.path.dirname(os.path.dirname(__file__))
        dialog_path = os.path.join(plugin_path, 'resources', 'qml', 'MainDialog.qml')
        self._dialog = self._application.createQmlComponent(dialog_path,
                                                            {'controller': self._controller})
        self._dialog.show()

    @pyqtSlot(str)
    def _onTokenChanged(self, token):
        if token is not None:
            self._controller.loadDocuments()
