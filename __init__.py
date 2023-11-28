# Copyright (c) 2023 Erwan MATHIEU

from .src import OnshapeFileProvider, OnshapeController


def getMetaData():
    return {}


def register(app):
    controller = OnshapeController.OnshapeController(app)
    return {
        "file_provider": OnshapeFileProvider.OnshapeFileProvider(controller),
    }
