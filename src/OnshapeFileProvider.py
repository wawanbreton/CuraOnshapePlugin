# Copyright (c) 2023 Erwan MATHIEU

import os

from PyQt6.QtCore import pyqtSlot

from UM.Application import Application
from UM.FileProvider import FileProvider
from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.Resources import Resources

from .OnshapeController import OnshapeController
from .OAuthController import OAuthController
from .api.OnshapeApi import OnshapeApi


class OnshapeFileProvider(FileProvider):

    def __init__(self, application):
        super().__init__()
        self.menu_item_display_text = 'From Onshape'
        self.shortcut = 'Ctrl+Alt+O'

        dir_path = os.path.dirname(__file__)
        dir_path = os.path.join(dir_path, '..')
        print(os.path.abspath(dir_path))
        Resources.addSearchPath(os.path.abspath(dir_path))

        i18n_catalog = i18nCatalog("onshape")

        if i18n_catalog.hasTranslationLoaded():
            Logger.info("OnShape Plugin translation loaded !")
        else:
            Logger.warning("OnShape Plugin translation not loaded")

        Application.getInstance().getPreferences().addPreference("plugin_onshape/tesselation_resolution", "moderate")

        self._application = application
        self._auth_controller = OAuthController(self._application)
        self._api = OnshapeApi()
        self._controller = OnshapeController(self._auth_controller, self._api)

        self._auth_controller.tokenChanged.connect(self._api.setToken)
        self._auth_controller.tokenChanged.connect(self._onTokenChanged)
        self._controller.partSelected.connect(self._onPartSelected)

    def run(self):
        plugin_path = os.path.dirname(os.path.dirname(__file__))
        dialog_path = os.path.join(plugin_path, 'resources', 'qml', 'MainDialog.qml')
        self._dialog = self._application.createQmlComponent(dialog_path,
                                                            {'controller': self._controller})
        self._dialog.show()

    @pyqtSlot(str)
    def _onTokenChanged(self, token):
        if token is not None:
            self._controller.loggedIn = True

    @pyqtSlot()
    def _onPartSelected(self):
        self._dialog.hide()
