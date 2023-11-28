//Copyright (C) 2022 Ultimaker B.V.
//Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Controls 2.3

import UM 1.2 as UM

Window
{
    id: root
    title: "Open file from Onshape"

    modality: Qt.ApplicationModal
    width: 1024 * screenScaleFactor
    height: 768 * screenScaleFactor
    minimumWidth: 800 * screenScaleFactor
    minimumHeight: 600 * screenScaleFactor

    Shortcut
    {
        sequence: "Esc"
        onActivated: root.close()
    }
    color: UM.Theme.getColor("main_background")

    Label
    {
        anchors.fill: parent
        text: "coucou !"
    }
}
