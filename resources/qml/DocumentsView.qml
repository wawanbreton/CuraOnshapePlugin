# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM
import Onshape 1.0 as Onshape


Rectangle
{
    id: root
    color: UM.Theme.getColor("main_background")

    property Onshape.DocumentsModel documentsModel
    signal elementSelected(Onshape.DocumentsModel subModel)
    readonly property real iconSizeFactor: 1.2

    RowLayout
    {
        id: header
        anchors
        {
            top: parent.top
            topMargin: UM.Theme.getSize("default_margin").height
            left: parent.left
            leftMargin: UM.Theme.getSize("default_margin").width
            right: parent.right
            rightMargin: anchors.leftMargin
        }

        spacing: UM.Theme.getSize("default_margin").width

        Cura.SecondaryButton
        {
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredHeight: UM.Theme.getSize("action_button").height
            Layout.preferredWidth: height


            enabled: !documentsModel.isRoot
            onClicked: root.parent.pop()

            leftPadding: UM.Theme.getSize("narrow_margin").width
            rightPadding: leftPadding
            iconSource: UM.Theme.getIcon("ArrowLeft")
            iconSize: height - leftPadding * 2
        }

        UM.Label
        {
            Layout.alignment: Qt.AlignVCenter
            Layout.fillWidth: true

            text: documentsModel.name
            font: UM.Theme.getFont("large")
        }
    }

    Rectangle
    {
        anchors.top: header.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").width
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: UM.Theme.getColor("detail_background")
        clip: true

        LoadingItem
        {
            anchors.fill: parent
            visible: !documentsModel.loaded
        }

        ListView
        {
            id: listView
            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").width
            spacing: UM.Theme.getSize("default_margin").height
            model: documentsModel.elements
            visible: documentsModel.loaded

            ScrollBar.vertical: UM.ScrollBar { id: verticalScrollBar }

            delegate: MouseArea
            {
                id: treeDelegate

                implicitWidth:
                {
                    var width = listView.width
                    var default_margin = UM.Theme.getSize("default_margin").width
                    width -= default_margin

                    if (verticalScrollBar.visible)
                    {
                        width -= default_margin
                    }

                    return width
                }
                implicitHeight: UM.Theme.getSize("card_icon").height * iconSizeFactor + 2 * UM.Theme.getSize("default_margin").height
                hoverEnabled: true

                onClicked: root.parent.push("DocumentsView.qml",
                                            {"documentsModel": modelData.childModel})

                Rectangle
                {
                    anchors.fill: parent
                    color: treeDelegate.containsMouse ? UM.Theme.getColor("action_button_hovered") : UM.Theme.getColor("main_background")

                    RowLayout
                    {
                        anchors.fill: parent
                        anchors.margins: UM.Theme.getSize("default_margin").width
                        spacing: UM.Theme.getSize("default_margin").width

                        Rectangle
                        {
                            color: modelData.hasThumbnail ? "white" : "transparent"
                            Layout.preferredWidth: UM.Theme.getSize("card_icon").width * iconSizeFactor
                            Layout.preferredHeight: UM.Theme.getSize("card_icon").height * iconSizeFactor

                            Image
                            {
                                visible: modelData.hasThumbnail
                                anchors.centerIn: parent
                                width: Math.min(implicitWidth, parent.width)
                                height: Math.min(implicitHeight, parent.height)
                                source: modelData.icon
                                fillMode: Image.PreserveAspectFit
                                mipmap: true
                            }

                            UM.ColorImage
                            {
                                visible: !modelData.hasThumbnail
                                anchors.fill: parent
                                source: modelData.icon
                                color: UM.Theme.getColor("icon")
                            }
                        }

                        ColumnLayout
                        {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            spacing: UM.Theme.getSize("narrow_margin").width

                            UM.Label
                            {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignLeft

                                text: modelData.name
                                font: UM.Theme.getFont("medium_bold")
                            }

                            UM.Label
                            {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignLeft

                                text: "%1\nLast updated: %2 by %3".arg(modelData.owner).arg(modelData.lastModifiedDate).arg(modelData.lastModifiedBy)
                                font: UM.Theme.getFont("default")
                            }
                        }
                    }
                }
            }
        }
    }
}
