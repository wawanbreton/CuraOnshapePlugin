# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtQml import qmlRegisterType

from .DocumentsModel import DocumentsModel

qmlRegisterType(DocumentsModel, "Onshape", 1, 0, "DocumentsModel")
