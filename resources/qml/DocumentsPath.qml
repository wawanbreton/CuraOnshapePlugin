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
        spacing: UM.Theme.getSize("default_margin").width

        Cura.SecondaryButton
        {
            id: button

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

            text: documentsModel.path.join(" > ")
            font: UM.Theme.getFont("large")
        }
    }
}
