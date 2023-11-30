# Copyright (c) 2023 Erwan MATHIEU

from UM.TaskManagement.HttpRequestManager import HttpRequestManager


class OnshapeApi:
    # The main Onshape URLs


    DEFAULT_REQUEST_TIMEOUT = 10  # seconds

    def __init__(self):
        self._http = HttpRequestManager.getInstance()
