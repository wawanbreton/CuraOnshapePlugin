# Copyright (c) 2023 Erwan MATHIEU

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

    ConnectionItem
    {
        anchors.fill: parent
        visible: controller.status === 'login'
    }

    LoadingItem
    {
        anchors.fill: parent
        visible: controller.status === 'loading'
    }

    DocumentsTree
    {
        anchors.fill: parent
        visible: controller.status === 'documents'
    }
}
