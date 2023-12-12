# Copyright (c) 2023 Erwan MATHIEU

from .src import OnshapeFileProvider


def getMetaData():
    return {}

def register(app):
    return {
        "file_provider": OnshapeFileProvider.OnshapeFileProvider(app),
    }
