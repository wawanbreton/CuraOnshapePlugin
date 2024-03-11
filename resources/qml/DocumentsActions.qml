import QtQuick 2.15

import UM 1.2 as UM
import Cura 1.0 as Cura

Item
{
    UM.I18nCatalog{id: catalog; name:"onshape"}

    implicitHeight: UM.get

    Cura.PrimaryButton
    {
        id: buttonDownload
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: UM.Theme.getSize("default_margin").height
        text: catalog.i18nc("@action:button", "Add to build plate")
        enabled: documentsListStack.currentItem.documentsModel.selectedItems.length > 0
        onClicked: controller.addToBuildPlate(documentsListStack.currentItem.documentsModel.selectedItems, false)
    }

    Cura.SecondaryButton
    {
        id: buttonDownloadGroup
        anchors.right: buttonDownload.left
        anchors.bottom: parent.bottom
        anchors.margins: UM.Theme.getSize("default_margin").height
        text: catalog.i18nc("@action:button", "Add and merge parts")
        enabled: documentsListStack.currentItem.documentsModel.selectedItems.length > 0
        onClicked: controller.addToBuildPlate(documentsListStack.currentItem.documentsModel.selectedItems, true)
    }

    Cura.TertiaryButton
    {
        id: buttonRefresh
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: UM.Theme.getSize("default_margin").height
        text: catalog.i18nc("@action:button", "Refresh")
        enabled: documentsListStack.currentItem.documentsModel.loaded && documentsListStack.currentItem.documentsModel.refreshable
        onClicked: documentsListStack.currentItem.documentsModel.refresh()
    }
}
