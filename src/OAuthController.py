# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING, Optional

import os
import json

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer

from UM.Qt.QtApplication import QtApplication
from cura.OAuth2.AuthorizationService import AuthorizationService
from cura.OAuth2.Models import OAuth2Settings

if TYPE_CHECKING:
    from cura.CuraApplication import CuraApplication


class OAuthController(QObject):
    """Controller in charge of the OAuth authentication to the Onshape remote API"""

    ROOT_AUTH_URL = 'https://oauth.onshape.com/oauth'

    tokenChanged = pyqtSignal(str)

    def __init__(self, application: "CuraApplication"):
        super().__init__()

        self._application: "CuraApplication" = application

        secrets_file_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'auth.json')
        with open(secrets_file_path, "rb") as secrets_file:
            def xor_encrypt_decrypt(data, key):
                return bytearray([data[i] ^ key[i % len(key)] for i in range(len(data))])

            encryption_key = '__ENCRYPTION_KEY__' # Replaced with actual key by runner
            if encryption_key.startswith('__'):
                # Dev mode
                auth_key_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'auth_key')
                encryption_key = open(auth_key_path, 'r').read()

            secrets_decrypted = xor_encrypt_decrypt(secrets_file.read(), encryption_key.encode('utf-8'))
            json_data = json.loads(secrets_decrypted.decode("utf-8"))

        callback_port = 35320
        oauth_settings = OAuth2Settings(
                    OAUTH_SERVER_URL=self.ROOT_AUTH_URL,
                    CALLBACK_PORT=callback_port,
                    CALLBACK_URL=f'http://localhost:{callback_port}/callback',
                    CLIENT_ID=json_data['client_id'],
                    CLIENT_SECRET=json_data['client_secret'],
                    CLIENT_SCOPES='OAuth2Read',
                    AUTH_DATA_PREFERENCE_KEY='plugin_onshape/auth_data',
                    AUTH_SUCCESS_REDIRECT='https://cad.onshape.com',
                    AUTH_FAILED_REDIRECT='https://cad.onshape.com'
                )

        self._authorization_service: AuthorizationService = AuthorizationService(oauth_settings, get_user_profile=False)
        self._authorization_service.initialize(self._application.getPreferences())
        self._authorization_service.onAuthStateChanged.connect(self._onLoginStateChanged)
        self._authorization_service.onAuthenticationError.connect(self._onLoginStateChanged)
        self._authorization_service.accessTokenChanged.connect(self._onAccessTokenChanged)

        self._refresh_timer: QTimer = QTimer()
        self._refresh_timer.timeout.connect(self._refreshTokenIfNeeded)
        self._refresh_timer.start(10000)

        QtApplication.getInstance().callLater(self._loadAuthData)

    def login(self) -> None:
        self._authorization_service.startAuthorizationFlow()

    def _onLoginStateChanged(self, logged_in: bool, error_message: Optional[str] = None):
        if logged_in:
            QtApplication.getInstance().getMainWindow().requestActivate()

    def _onAccessTokenChanged(self) -> None:
        self.tokenChanged.emit(self._authorization_service.getAccessToken())

    @pyqtSlot()
    def _refreshTokenIfNeeded(self) -> None:
        # Just call getAccessToken, which will start a refresh if required
        self._authorization_service.getAccessToken()

    def _loadAuthData(self) -> None:
        self._authorization_service.loadAuthDataFromPreferences()
        self._onAccessTokenChanged()

