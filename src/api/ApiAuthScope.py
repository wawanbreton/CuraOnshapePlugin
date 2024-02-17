# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING

from UM.Logger import Logger
from UM.TaskManagement.HttpRequestScope import HttpRequestScope

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkRequest


class ApiAuthScope(HttpRequestScope):
    """HTTP authentication scope using a given access token"""

    def __init__(self):
        super().__init__()
        self._token: str = None

    def setToken(self, token: str) -> None:
        self._token = token

    def requestHook(self, request: 'QNetworkRequest') -> None:
        super().requestHook(request)

        if self._token is not None:
            self.addHeaders(request, { 'Authorization': 'Bearer {}'.format(self._token) })
        else:
            Logger.error('User is not logged in for Onshape API request to {url}'.format(url = request.url().toDisplayString()))
