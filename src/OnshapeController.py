# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty, QAbstractItemModel

from .model.OnshapeDocumentsModel import OnshapeDocumentsModel
from .data.OnshapeRoot import OnshapeRoot
from .data.OnshapeDocumentsTreeNode import OnshapeDocumentsTreeNode


class OnshapeController(QObject):

    def __init__(self, auth_controller, api):
        super().__init__(parent = None)

        self._auth_controller = auth_controller
        self._api = api
        self._logged_in = False
        self._documents_model = OnshapeDocumentsModel(OnshapeDocumentsTreeNode(OnshapeRoot()),
                                                      self._api)

    loggedInChanged = pyqtSignal()

    def setLoggedIn(self, logged_in):
        self._logged_in = logged_in
        self.loggedInChanged.emit()

    @pyqtProperty(bool, notify = loggedInChanged, fset = setLoggedIn)
    def loggedIn(self):
        return self._logged_in

    @pyqtProperty(QAbstractItemModel, constant = True)
    def documentsModel(self):
        return self._documents_model

    @pyqtSlot()
    def login(self):
        self._auth_controller.login()
