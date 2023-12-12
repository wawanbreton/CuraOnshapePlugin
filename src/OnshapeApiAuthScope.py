# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtNetwork import QNetworkRequest

from UM.Logger import Logger
from UM.TaskManagement.HttpRequestScope import HttpRequestScope


class OnshapeApiAuthScope(HttpRequestScope):

    def __init__(self):
        super().__init__()
        self._token = None

    def setToken(self, token):
        self._token = token

    def requestHook(self, request: QNetworkRequest):
        super().requestHook(request)

        if self._token is not None:
            self.addHeaders(request, { "Authorization": "Bearer {}".format(self._token) })
        else:
            Logger.error("User is not logged in for Onshape API request to {url}".format(url = request.url().toDisplayString()))
