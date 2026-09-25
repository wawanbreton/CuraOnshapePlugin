# Copyright (c) 2023 Erwan MATHIEU

from typing import Any, Dict, List

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal

from .ConfigurationOption import ConfigurationOption


class ConfigurationParameter(QObject):
    """Represents one Onshape configuration input exposed to QML"""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(parent = None)
        self._parameter_id = data['id']
        self._name = data['name']
        self._options = [
            ConfigurationOption(option['name'], option['value'])
            for option in data['options']
        ]
        self._selected_index = next(
            (index for index, option in enumerate(self._options) if option.value == data['value']), 0
        )

    @pyqtProperty(str, constant = True)
    def parameterId(self) -> str:
        return self._parameter_id

    @pyqtProperty(str, constant = True)
    def name(self) -> str:
        return self._name

    @pyqtProperty(list, constant = True)
    def options(self) -> List[ConfigurationOption]:
        return self._options

    selectedIndexChanged = pyqtSignal()

    def setSelectedIndex(self, selected_index: int) -> None:
        if selected_index != self._selected_index and 0 <= selected_index < len(self._options):
            self._selected_index = selected_index
            self.selectedIndexChanged.emit()

    @pyqtProperty(int, notify = selectedIndexChanged, fset = setSelectedIndex)
    def selectedIndex(self) -> int:
        return self._selected_index

    @property
    def selectedValue(self) -> str:
        if 0 <= self._selected_index < len(self._options):
            return self._options[self._selected_index].value
        return ''
