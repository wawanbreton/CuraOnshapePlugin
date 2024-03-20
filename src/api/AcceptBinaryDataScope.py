# Copyright (c) 2023 Erwan MATHIEU

from typing import TYPE_CHECKING

from UM.TaskManagement.HttpRequestScope import HttpRequestScope

if TYPE_CHECKING:
    from PyQt6.QtNetwork import QNetworkRequest


class AcceptBinaryDataScope(HttpRequestScope):
    """Simple HTTP scope adding a header to allow receiving binary data"""

    def __init__(self, base: 'HttpRequestScope'):
        super().__init__()
        self.base: HttpRequestScope = base

    def requestHook(self, request: 'QNetworkRequest') -> None:
        # not calling super().request_hook() because base will do that.
        self.base.requestHook(request)
        self.addHeaders(request, { 'accept': 'application/octet-stream' })
