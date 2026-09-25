# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtCore import QObject, pyqtProperty


class ConfigurationOption(QObject):
    """Represents one selectable value for an Onshape configuration input"""

    def __init__(self, name: str, value: str):
        super().__init__(parent = None)
        self._name = name
        self._value = value

    @pyqtProperty(str, constant = True)
    def name(self) -> str:
        return self._name

    @pyqtProperty(str, constant = True)
    def value(self) -> str:
        return self._value
