# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import QObject, pyqtSlot

from UM.TaskManagement.HttpRequestManager import HttpRequestManager
from UM.TaskManagement.HttpRequestScope import JsonDecoratorScope

from .OnshapeApiAuthScope import OnshapeApiAuthScope


class OnshapeApi(QObject):
    API_ROOT = 'https://cad.onshape.com/api/v6'
    DEFAULT_REQUEST_TIMEOUT = 10  # seconds

    def __init__(self):
        super().__init__(parent = None)
        self._http = HttpRequestManager.getInstance()
        self._auth_scope = OnshapeApiAuthScope()
        self._scope = JsonDecoratorScope(self._auth_scope)

    @pyqtSlot(str)
    def setToken(self, token):
        self._auth_scope.setToken(token)
        print('################################################## token set !')

        def callback(answer):
            print('coucou', answer.readAll())

        def error_cb(request, error):
            print('pas bien', request, error)

        if token is not None:
            self.listDocuments(callback, error_cb)

    def listDocuments(self, on_finished, on_error):
        url = f'{self.API_ROOT}/documents'

        self._http.get(url,
                       scope = self._scope,
                       callback = on_finished,
                       error_callback = on_error,
                       timeout = self.DEFAULT_REQUEST_TIMEOUT)
