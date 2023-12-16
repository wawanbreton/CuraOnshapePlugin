# Copyright (c) 2023 Erwan MATHIEU

from .OnshapeElement import OnshapeElement


class OnshapeFolder(OnshapeElement):

    def __init__(self, data):
        super().__init__(data)
