# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM


RowLayout
{
    id: root
    spacing: UM.Theme.getSize("default_margin").width

    Cura.SecondaryButton
    {
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

    UM.Label
    {
        Layout.alignment: Qt.AlignVCenter
        Layout.fillWidth: true

        text: documentsModel.name
        font: UM.Theme.getFont("large")
    }
}
