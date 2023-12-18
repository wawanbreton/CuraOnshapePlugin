# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtNetwork import QNetworkRequest

from UM.TaskManagement.HttpRequestScope import HttpRequestScope


class AcceptBinaryDataScope(HttpRequestScope):

    def __init__(self, base):
        super().__init__()
        self.base = base

    def requestHook(self, request: QNetworkRequest):
        # not calling super().request_hook() because base will do that.
        self.base.requestHook(request)
        self.addHeaders(request, { "accept": "application/octet-stream" })
