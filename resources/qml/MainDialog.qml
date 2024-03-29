# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import UM 1.2 as UM
import Cura 1.5 as Cura

Window
{
    id: root
    title: catalog.i18nc("@title:window", "Open model from Onshape")

    modality: Qt.ApplicationModal
    width: 1024 * screenScaleFactor
    height: 768 * screenScaleFactor
    minimumWidth: 800 * screenScaleFactor
    minimumHeight: 600 * screenScaleFactor

    UM.I18nCatalog{id: catalog; name:"onshape"}

    Shortcut
    {
        sequence: "Esc"
        onActivated: root.close()
    }
    color: UM.Theme.getColor("main_background")

    ConnectionItem
    {
        anchors.fill: parent
        visible: !controller.loggedIn
    }

    Rectangle
    {
        color: UM.Theme.getColor("main_background")
        anchors.fill: parent
        visible: controller.loggedIn

        ColumnLayout
        {
            anchors.fill: parent
            spacing: 0

            DocumentsPath
            {
                Layout.fillWidth: true
                documentsModel: documentsListStack.currentItem.documentsModel
            }

            StackView
            {
                id: documentsListStack
                Layout.fillHeight: true
                Layout.fillWidth: true

                initialItem: DocumentsView
                {
                    documentsModel: controller.documentsModel
                }
            }

            DocumentsActions
            {
                Layout.fillWidth: true
                Layout.preferredHeight: UM.Theme.getSize("action_button").height + UM.Theme.getSize("default_margin").height * 2
            }
        }
    }
}
