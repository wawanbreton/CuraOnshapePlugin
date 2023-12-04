# Copyright (c) 2023 Erwan MATHIEU

import os
import json

from PyQt6.QtCore import QObject, pyqtSlot

from UM.Logger import Logger
from cura.OAuth2.AuthorizationService import AuthorizationService
from cura.OAuth2.Models import OAuth2Settings


class OAuthController(QObject):

    ROOT_AUTH_URL = 'https://oauth.onshape.com/oauth'

    def __init__(self, application):
        super().__init__()

        self._application = application
        self._logged_in = False

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

        self._authorization_service = AuthorizationService(oauth_settings)
        self._authorization_service.initialize(self._application.getPreferences())
        self._authorization_service.onAuthStateChanged.connect(self._onLoginStateChanged)
        self._authorization_service.onAuthenticationError.connect(self._onLoginStateChanged)
        self._authorization_service.accessTokenChanged.connect(self._onAccessTokenChanged)
        self._authorization_service.loadAuthDataFromPreferences()

    @pyqtSlot()
    def login(self):
        self._authorization_service.startAuthorizationFlow()

    def _onLoginStateChanged(self, logged_in, error_message=None):
        # if error_message:
        #     if self._error_message:
        #         self._error_message.hide()
        #     Logger.log("w", "Failed to login: %s", error_message)
        #     self._error_message = Message(error_message,
        #                                   title = i18n_catalog.i18nc("@info:title", "Login failed"),
        #                                   message_type = Message.MessageType.ERROR)
        #     self._error_message.show()
        #     self._logged_in = False
        #     self.loginStateChanged.emit(False)
        #     if self._update_timer.isActive():
        #         self._update_timer.stop()
        #     return

        Logger.info(f'ONSHAPE PLUGIN Onshape account logged in {logged_in}')
        if logged_in != self._logged_in:
            self._logged_in = logged_in
            Logger.debug(self._authorization_service.getAccessToken())
            #self.loginStateChanged.emit(logged_in)

    def _onAccessTokenChanged(self):
        Logger.debug('ONSHAPE PLUGIN access token changed', self._authorization_service.getAccessToken())
        #self.accessTokenChanged.emit()
