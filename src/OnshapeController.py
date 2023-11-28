# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty


class OnshapeController(QObject):

    def __init__(self, application) -> None:
        super().__init__(parent = None)

        self._application = application
        #self._api = DigitalFactoryApiClient(self._application, on_error = lambda error: Logger.log("e", str(error)), projects_limit_per_page = 20)
