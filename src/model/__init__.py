# Copyright (c) 2023 Erwan MATHIEU

from PyQt6.QtQml import qmlRegisterType

from .OnshapeDocumentsModel import OnshapeDocumentsModel

qmlRegisterType(OnshapeDocumentsModel, "Onshape", 1, 0, "DocumentsModel")
