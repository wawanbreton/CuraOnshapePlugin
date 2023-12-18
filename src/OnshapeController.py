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
        self._status = 'login'
        self._documents_model = OnshapeDocumentsModel(OnshapeDocumentsTreeNode(OnshapeRoot()),
                                                      self._api)

    statusChanged = pyqtSignal()

    @pyqtProperty(str, notify = statusChanged)
    def status(self):
        return self._status

    modelChanged = pyqtSignal()

    @pyqtProperty(QAbstractItemModel, notify = modelChanged)
    def documentsModel(self):
        return self._documents_model

    def _setStatus(self, status):
        self._status = status
        self.statusChanged.emit()

    @pyqtSlot()
    def login(self):
        self._auth_controller.login()

    def loadDocuments(self):
        def on_finished(answer):
            self._documents_model.setNodeChildren(answer.getTree().children)
            self.modelChanged.emit()

        def on_error(request, error):
            print('pas bien', request, error)

        self._setStatus('documents')
        self._api.listDocuments(on_finished, on_error)
