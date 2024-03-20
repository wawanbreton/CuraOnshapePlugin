# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING

import os

from PyQt6.QtCore import pyqtSlot

from UM.FileProvider import FileProvider
from UM.i18n import i18nCatalog
from UM.Logger import Logger
from UM.Resources import Resources

from .OnshapeController import OnshapeController
from .OAuthController import OAuthController
from .api.OnshapeApi import OnshapeApi

if TYPE_CHECKING:
    from cura.CuraApplication import CuraApplication


class OnshapeFileProvider(FileProvider):
    """
    Main entry point of the plugin, instanciated by the application. It handles the authentication
    controller, the API access controller, and provides the UI.
    """

    def __init__(self, application: "CuraApplication"):
        super().__init__()
        i18n_catalog = i18nCatalog("onshape")

        self.menu_item_display_text: str = i18n_catalog.i18nc("@menu", "From Onshape")
        self.shortcut: str = 'Ctrl+Alt+O'

        dir_path = os.path.dirname(__file__)
        dir_path = os.path.join(dir_path, '..')
        print(os.path.abspath(dir_path))
        Resources.addSearchPath(os.path.abspath(dir_path))

        if i18n_catalog.hasTranslationLoaded():
            Logger.info("OnShape Plugin translation loaded !")
        else:
            Logger.warning("OnShape Plugin translation not loaded")

        application.getPreferences().addPreference("plugin_onshape/tesselation_resolution", "moderate")

        self._application: "CuraApplication" = application
        self._auth_controller: OAuthController = OAuthController(self._application)
        self._api: OnshapeApi = OnshapeApi()
        self._controller: OnshapeController = OnshapeController(self._auth_controller, self._api)

        self._auth_controller.tokenChanged.connect(self._api.setToken)
        self._auth_controller.tokenChanged.connect(self._onTokenChanged)
        self._controller.partSelected.connect(self._onPartSelected)

    def run(self) -> None:
        """Main entry point called by the application when the users asks for opening Onshape"""
        plugin_path = os.path.dirname(os.path.dirname(__file__))
        dialog_path = os.path.join(plugin_path, 'resources', 'qml', 'MainDialog.qml')
        self._dialog = self._application.createQmlComponent(dialog_path,
                                                            {'controller': self._controller})
        self._dialog.show()

    @pyqtSlot(str)
    def _onTokenChanged(self, token: str) -> None:
        if token is not None:
            self._controller.loggedIn = True

    @pyqtSlot()
    def _onPartSelected(self) -> None:
        self._dialog.hide()
