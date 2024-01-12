# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM
import Onshape 1.0 as Onshape


Item
{
    property Onshape.DocumentsModel documentsModel

    id: root
    implicitHeight: row.implicitHeight + 2 * UM.Theme.getSize("default_margin").width

    RowLayout
    {
        id: row

        anchors.fill: parent
        anchors.margins: UM.Theme.getSize("default_margin").width
        spacing: 0

        Cura.SecondaryButton
        {
            Layout.rightMargin: UM.Theme.getSize("default_margin").width
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredHeight: UM.Theme.getSize("action_button").height
            Layout.preferredWidth: height

            enabled: !documentsModel.isRoot
            onClicked: documentsListStack.pop()

            leftPadding: UM.Theme.getSize("narrow_margin").width
            rightPadding: leftPadding
            iconSource: UM.Theme.getIcon("ArrowLeft")
            iconSize: height - leftPadding * 2
        }

        Repeater
        {
            model: documentsModel.path

            RowLayout
            {
                spacing: 0

                UM.Label
                {
                    text: modelData
                    font: UM.Theme.getFont("large")
                }

                UM.ColorImage
                {
                    source: UM.Theme.getIcon("ChevronSingleRight")
                    height: UM.Theme.getFont("large").pixelSize
                    width: height
                    color: UM.Theme.getColor("text")
                    visible: index < documentsModel.path.length - 1
                }
            }
        }

        Item
        {
            Layout.fillWidth: true
        }

        Button
        {
            id: buttonSettings

            implicitHeight: UM.Theme.getSize("action_button").height
            implicitWidth: implicitHeight
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredHeight: implicitHeight
            Layout.preferredWidth: implicitWidth

            background: Rectangle
            {
                radius: Math.round(width * 0.5)
                color: UM.Theme.getColor(buttonSettings.hovered ? "toolbar_button_hover" : "toolbar_background")
            }

            contentItem: Item
            {
                UM.ColorImage
                {
                    anchors.centerIn: parent
                    implicitWidth: UM.Theme.getSize("action_button_icon").width
                    implicitHeight: UM.Theme.getSize("action_button_icon").height
                    source: UM.Theme.getIcon("Settings")
                    color: UM.Theme.getColor("icon")
                }
            }

            onClicked: componentSettings.createObject().show()
        }

        Component
        {
            id: componentSettings

            SettingsDialog
            {
                modality: Qt.ApplicationModal
            }
        }
    }
}
