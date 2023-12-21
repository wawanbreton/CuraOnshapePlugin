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
    property variant catalog: UM.I18nCatalog { name: "cura" }

    ColumnLayout
    {
        anchors.centerIn: parent
        spacing: UM.Theme.getSize("default_margin").height

        Image
        {
            source: UM.Theme.getColor("main_background").hslLightness > 0.5 ? "../images/onshape-logo-full.svg" : "../images/onshape-logo-full-dark.svg"
            Layout.maximumHeight: 300
            fillMode: Image.PreserveAspectFit
        }

        Label
        {
            text: "Sign in to your Onshape account to access your documents"
            color: UM.Theme.getColor("text_default")
            font: UM.Theme.getFont("large_bold")
            Layout.alignment: Qt.AlignHCenter
        }

        Cura.PrimaryButton
        {
            text: catalog.i18nc("@button", "Sign in")
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: UM.Theme.getSize("account_button").width
            Layout.preferredHeight: UM.Theme.getSize("account_button").height
            fixedWidthMode: true
            onClicked: controller.login()
        }
    }
}
