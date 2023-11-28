# Copyright (c) 2023 Erwan MATHIEU

import os

from UM.FileProvider import FileProvider

from cura.CuraApplication import CuraApplication


class OnshapeFileProvider(FileProvider):

    def __init__(self, controller):
        super().__init__()
        self.menu_item_display_text = "From Onshape"
        self.shortcut = "Ctrl+Alt+O"
        self._controller = controller

    def run(self) -> None:
        plugin_path = os.path.dirname(os.path.dirname(__file__))
        dialog_path = os.path.join(plugin_path, "resources", "qml", "OnshapeMainDialog.qml")
        app = CuraApplication.getInstance()
        self._dialog = app.createQmlComponent(dialog_path, {"controller": self._controller})
        self._dialog.show()
