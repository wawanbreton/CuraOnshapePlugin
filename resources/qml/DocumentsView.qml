# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM
import Onshape 1.0 as Onshape


Rectangle
{
    id: root
    color: UM.Theme.getColor("main_background")

    property Onshape.DocumentsModel documentsModel
    signal elementSelected(Onshape.DocumentsModel subModel)
    readonly property real iconSizeFactor: 1.2

    DocumentsPath
    {
        id: header
        anchors
        {
            top: parent.top
            topMargin: UM.Theme.getSize("default_margin").height
            left: parent.left
            leftMargin: UM.Theme.getSize("default_margin").width
            right: parent.right
            rightMargin: anchors.leftMargin
        }
    }

    Rectangle
    {
        anchors.top: header.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").width
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: UM.Theme.getColor("detail_background")
        clip: true

        LoadingItem
        {
            anchors.fill: parent
            visible: !documentsModel.loaded
        }

        ListView
        {
            id: listView
            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").width
            spacing: UM.Theme.getSize("default_margin").height
            model: documentsModel.elements
            visible: documentsModel.loaded
            clip: true

            ScrollBar.vertical: UM.ScrollBar { id: verticalScrollBar }

            delegate: DocumentCard { }
        }
    }

    Component.onCompleted: loadDocumentsIfVisible()
    onVisibleChanged: loadDocumentsIfVisible()

    function loadDocumentsIfVisible() { if(visible) { documentsModel.load() } }
}
