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
            id: loadingIndicator

            Layout.preferredWidth: UM.Theme.getSize("card_icon").width
            Layout.preferredHeight: UM.Theme.getSize("card_icon").height
            Layout.alignment: Qt.AlignHCenter
            source: UM.Theme.getIcon("ArrowDoubleCircleRight")
            color: UM.Theme.getColor("text_default")

            RotationAnimator
            {
                target: loadingIndicator
                from: 0
                to: 360
                duration: 2000
                loops: Animation.Infinite
                running: true
                alwaysRunToEnd: true
            }
        }

        Label
        {
            Layout.fillWidth: true
            text: catalog.i18nc("@label",  "Loading ...")
            color: UM.Theme.getColor("text_default")
            font: UM.Theme.getFont("large_bold")
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
