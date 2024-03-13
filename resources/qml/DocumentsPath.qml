# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM


Item
{
    property var documentsModel

    id: root
    implicitHeight: row.implicitHeight + 2 * UM.Theme.getSize("default_margin").width

    RowLayout
    {
        id: row

        anchors.fill: parent
        anchors.margins: UM.Theme.getSize("default_margin").width
        spacing: 0

        Repeater
        {
            model: documentsModel.path

            RowLayout
            {
                spacing: 0

                UM.Label
                {
                    text: modelData
                    visible: modelData.length > 0
                    font: UM.Theme.getFont("large")

                    MouseArea
                    {
                        anchors.fill: parent
                        hoverEnabled: true
                        onContainsMouseChanged: parent.font.underline = containsMouse
                        onClicked: popToIndex(index)
                    }
                }

                UM.ColorImage
                {
                    source: UM.Theme.getIcon("House")
                    height: UM.Theme.getSize("large_button_icon").width
                    width: height
                    color: UM.Theme.getColor(imageMouseArea.containsMouse ? "text_link" : "text")
                    visible: modelData.length === 0

                    MouseArea
                    {
                        id: imageMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: popToIndex(index)
                    }
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

    function popToIndex(index)
    {
        documentsListStack.pop(documentsListStack.get(index))
    }
}
