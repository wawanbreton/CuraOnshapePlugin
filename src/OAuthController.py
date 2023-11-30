# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import QObject, pyqtSlot

from cura.OAuth2.AuthorizationService import AuthorizationService
from cura.OAuth2.Models import OAuth2Settings, UserProfile


class OAuthController(QObject):

    ROOT_AUTH_URL = "https://oauth.onshape.com/oauth"

    def __init__(self):
        super().__init__()

        callback_port = 35320
        oauth_settings = OAuth2Settings(
                    OAUTH_SERVER_URL=self.ROOT_AUTH_URL,
                    CALLBACK_PORT=callback_port,
                    CALLBACK_URL="http://localhost:{}/callback".format(callback_port),
                    CLIENT_ID="QHSPHFNZDYC2U4ZOPXMLW54E3K4R42LBH2YZNTQ=",
                )

        self._authorization_service = AuthorizationService(oauth_settings)

    @pyqtSlot()
    def login(self):
        print("gogogo")
        self._authorization_service.startAuthorizationFlow()
