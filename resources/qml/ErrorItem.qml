# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import UM 1.5 as UM


Item
{
    id: root

    UM.I18nCatalog{id: catalog; name:"onshape"}

    ColumnLayout
    {
        anchors.centerIn: parent

        UM.ColorImage
        {
            Layout.preferredWidth: UM.Theme.getSize("card_icon").width
            Layout.preferredHeight: UM.Theme.getSize("card_icon").height
            Layout.alignment: Qt.AlignHCenter
            source: UM.Theme.getIcon("ErrorBadge", "low")
            color: UM.Theme.getColor("error")
        }

        Label
        {
            Layout.maximumWidth: root.width
            text: catalog.i18nc("@label",  "Request error: %1").arg(documentsModel.error)
            color: UM.Theme.getColor("text_default")
            font: UM.Theme.getFont("large_bold")
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.Wrap
        }
    }
}
