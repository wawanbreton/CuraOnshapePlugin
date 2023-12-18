# Copyright (c) 2023 Erwan MATHIEU


class OnshapeBaseModel:

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def loadChildren(self, api, on_finished, on_error):
        return NotImplementedError(f'Children of {self.__class__} are not to be loaded')

    def getIcon(self):
        return ''
