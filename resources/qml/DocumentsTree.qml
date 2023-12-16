# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import UM 1.5 as UM


Rectangle
{
    id: root
    color: UM.Theme.getColor("detail_background")

    ListView
    {
        id: listView
        anchors.fill: parent
        anchors.margins: UM.Theme.getSize("default_margin").width
        spacing: UM.Theme.getSize("default_margin").height
        model: controller.documentsModel.elements

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
            implicitHeight: UM.Theme.getSize("card_icon").height + 2 * UM.Theme.getSize("default_margin").height
            hoverEnabled: true

            //onClicked: { treeView.toggleExpanded(row) }

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
                        Layout.preferredWidth: UM.Theme.getSize("card_icon").width
                        Layout.preferredHeight: UM.Theme.getSize("card_icon").height

                        Image
                        {
                            anchors.centerIn: parent
                            width: Math.min(implicitWidth, parent.width)
                            height: Math.min(implicitHeight, parent.height)
                            source: modelData.icon
                            fillMode: Image.PreserveAspectFit
                            mipmap: true
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
