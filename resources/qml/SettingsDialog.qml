# Copyright (c) 2024 Erwan MATHIEU

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import UM 1.2 as UM
import Cura 1.0 as Cura

Window
{
    width: column.implicitWidth + 4 * UM.Theme.getSize("default_margin").width
    height: column.implicitHeight + 4 * UM.Theme.getSize("default_margin").width

    Rectangle
    {
        color: UM.Theme.getColor("detail_background")
        anchors.fill: parent

        Rectangle
        {
            color: UM.Theme.getColor("main_background")
            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").width

            ColumnLayout
            {
                id: column

                anchors.fill: parent
                anchors.margins: UM.Theme.getSize("default_margin").width

                Label
                {
                    color: UM.Theme.getColor("text")
                    font: UM.Theme.getFont("medium_bold")
                    text: "Tesselation resolution"
                    Layout.fillWidth: true
                }

                ButtonGroup
                {
                    id: resolutionGroup
                    buttons: [radioResolutionCoarse, radioResolutionModerate, radioResolutionFine]
                }

                Cura.RadioButton
                {
                    id: radioResolutionCoarse
                    text: "Coarse"
                    checked: UM.Preferences.getValue("plugin_onshape/tesselation_resolution") === "coarse"
                    onClicked: UM.Preferences.setValue("plugin_onshape/tesselation_resolution", "coarse")
                }

                Cura.RadioButton
                {
                    id: radioResolutionModerate
                    text: "Moderate"
                    checked: UM.Preferences.getValue("plugin_onshape/tesselation_resolution") === "moderate"
                    onClicked: UM.Preferences.setValue("plugin_onshape/tesselation_resolution", "moderate")
                }

                Cura.RadioButton
                {
                    id: radioResolutionFine
                    text: "Fine"
                    checked: UM.Preferences.getValue("plugin_onshape/tesselation_resolution") === "fine"
                    onClicked: UM.Preferences.setValue("plugin_onshape/tesselation_resolution", "fine")
                }
            }
        }
    }
}
