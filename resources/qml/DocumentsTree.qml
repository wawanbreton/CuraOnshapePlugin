# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.10
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import UM 1.5 as UM


Item
{
    id: root

    Label
    {
        anchors.fill: parent
        text: "Voici les docs !!!"
        color: UM.Theme.getColor("text_default")
        font: UM.Theme.getFont("large_bold")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
