# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM


Item
{
    id: root

    ColumnLayout
    {
        anchors.centerIn: parent
        spacing: UM.Theme.getSize("default_margin").height

        Image
        {
            source: "../images/onshape-logo-full.svg"
            Layout.maximumHeight: 300
            fillMode: Image.PreserveAspectFit
        }

        Label
        {
            text: "Login to your Onshape account to access your documents"
            color: UM.Theme.getColor("text_default")
            font: UM.Theme.getFont("large_bold")
            Layout.alignment: Qt.AlignHCenter
        }

        Cura.PrimaryButton
        {
            text: "Login to Onshape"
            Layout.alignment: Qt.AlignHCenter
            onClicked: controller.login()
        }
    }
}
