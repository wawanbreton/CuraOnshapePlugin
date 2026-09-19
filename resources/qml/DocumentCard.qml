# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM


MouseArea
{
    id: root

    UM.I18nCatalog{id: catalog; name:"onshape"}

    implicitWidth:
    {
        var width = listView.width
        var default_margin = UM.Theme.getSize("default_margin").width

        if (verticalScrollBar.visible)
        {
            width -= 2 * default_margin
        }

        return width
    }
    implicitHeight: UM.Theme.getSize("card_icon").height * iconSizeFactor + 2 * UM.Theme.getSize("default_margin").height

    hoverEnabled: true
    enabled: modelData.hasChildren || modelData.isDownloadable // Should actually always be true...
    onClicked:
    {
        if(isInside(checkBoxSelected, mouse.x, mouse.y))
        {
            return
        }

        trigger()
    }

    Rectangle
    {
        anchors.fill: parent
        color: root.containsMouse ? UM.Theme.getColor("action_button_hovered") : UM.Theme.getColor("main_background")

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
                Layout.alignment: Qt.AlignVCenter
                spacing: UM.Theme.getSize("narrow_margin").height

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
                    visible: text.length > 0

                    font: UM.Theme.getFont("default")
                    text:
                    {
                        var texts = []
                        if(modelData.shortDesc)
                        {
                            texts.push(modelData.shortDesc)
                        }
                        if(modelData.lastModifiedDate)
                        {
                            var text_updated = catalog.i18nc("@label", "Last updated: %1").arg(modelData.lastModifiedDate)
                            if(modelData.lastModifiedBy)
                            {
                                text_updated += catalog.i18nc("@label", " by %1").arg(modelData.lastModifiedBy)
                            }
                            texts.push(text_updated)
                        }

                        return texts.join("\n")
                    }
                }
            }

            UM.CheckBox
            {
                id: checkBoxSelected
                visible: modelData.isDownloadable
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredWidth: 130
                text: catalog.i18nc("@action:button", "Add to selection")
                checked: modelData.selected
                onClicked: modelData.selected = checked
            }
        }

        Cura.PrimaryButton
        {
            id: buttonSetAsDefault
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: UM.Theme.getSize("default_margin").height
            text: catalog.i18nc("@action:button", "Open and set as default")
            visible: modelData.settableAsDefault
            onClicked:
            {
                modelData.setAsDefault();
                root.trigger();
            }
        }
    }

    function trigger()
    {
        if(modelData.hasChildren)
        {
            documentsListStack.push("DocumentsView.qml", {"documentsModel": modelData.childModel})
        }
        else if(modelData.isDownloadable)
        {
            modelData.selected = !modelData.selected
        }
    }

    function isInside(item, x, y)
    {
        var point = item.mapFromItem(root, x, y)
        return item.visible && point.x >= 0 && point.x <= item.width && point.y >= 0 && point.y <= item.height
    }
}
