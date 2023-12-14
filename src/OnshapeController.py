# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, pyqtProperty


class OnshapeController(QObject):

    def __init__(self, auth_controller, api):
        super().__init__(parent = None)

        self._auth_controller = auth_controller
        self._api = api
        self._status = 'login'

    statusChanged = pyqtSignal()

    @pyqtProperty(str, notify = statusChanged)
    def status(self):
        return self._status

    def _setStatus(self, status):
        self._status = status
        self.statusChanged.emit()

    @pyqtSlot()
    def login(self):
        self._auth_controller.login()

    def loadDocuments(self):
        def on_finished(answer):
            def print_node(node, level):
                if node.element is not None:
                    level_str = "--" * level
                    print(f'{level_str} {node.element.name}')
                for child in node.children:
                    print_node(child, level + 1)

            print_node(answer.getTree(), 0)
            self._setStatus('documents')

        def on_error(request, error):
            print('pas bien', request, error)

        self._setStatus('loading')
        self._api.listDocuments(on_finished, on_error)
