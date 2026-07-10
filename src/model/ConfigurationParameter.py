# Copyright (c) 2023 Erwan MATHIEU

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal


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


class ConfigurationParameter(QObject):
    """Represents one Onshape configuration input exposed to QML"""

    def __init__(self, data: Dict[str, Any], current_value: Optional[str]):
        super().__init__(parent = None)
        self._parameter_id = data['parameterId']
        self._name = data.get('parameterName', self._parameter_id)
        self._options = [
            ConfigurationOption(option.get('optionName', option['option']), option['option'])
            for option in data.get('options', [])
        ]

        selected_value = current_value or data.get('defaultValue')
        self._selected_index = self._indexOfValue(selected_value)

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

    def _indexOfValue(self, value: Optional[str]) -> int:
        for index, option in enumerate(self._options):
            if option.value == value:
                return index
        return 0
