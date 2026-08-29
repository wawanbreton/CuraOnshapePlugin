# Copyright (c) 2023 Erwan MATHIEU

import QtQuick 2.15
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.15

import Cura 1.5 as Cura
import UM 1.5 as UM


Item
{
    id: root

    property var documentsModel
    signal elementSelected(var subModel)
    readonly property real iconSizeFactor: 1.2

    Rectangle
    {
        anchors.fill: parent
        color: UM.Theme.getColor("detail_background")
        clip: true

        LoadingItem
        {
            anchors.fill: parent
            visible: !documentsModel.loaded && !documentsModel.hasError
        }

        ErrorItem
        {
            anchors.fill: parent
            visible: documentsModel.hasError
        }

        ListView
        {
            id: listView
            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").width
            spacing: UM.Theme.getSize("default_margin").height
            model: documentsModel.elements
            visible: documentsModel.loaded && !documentsModel.hasError
            clip: true

            ScrollBar.vertical: UM.ScrollBar { id: verticalScrollBar }

            footer: LoadingItem
            {
                width: listView.width
                height: documentsModel.isLoadingNextPage ? UM.Theme.getSize("card_icon").height * root.iconSizeFactor + 2 * UM.Theme.getSize("default_margin").height : 0
                visible: documentsModel.isLoadingNextPage
            }

            delegate: DocumentCard { }

            // Saved scroll position to restore after a next-page append
            property real savedContentY: 0
            property bool restoringScroll: false

            Connections
            {
                target: documentsModel

                function onElementsChanged()
                {
                    if(listView.savedContentY > 0)
                    {
                        // A next-page append triggered this change; restore the position.
                        // Use Qt.callLater so the layout has settled before we set contentY.
                        var posToRestore = listView.savedContentY
                        listView.savedContentY = 0
                        Qt.callLater(function() { listView.contentY = posToRestore })
                    }
                }
            }

            onContentYChanged:
            {
                // When the user scrolls close to the bottom, load the next page
                var threshold = UM.Theme.getSize("card_icon").height * root.iconSizeFactor * 2
                if (documentsModel.hasMorePages && !documentsModel.isLoadingNextPage &&
                    contentY + height >= contentHeight - threshold)
                {
                    listView.savedContentY = contentY
                    documentsModel.loadNextPage()
                }
            }
        }
    }

    Component.onCompleted: loadDocumentsIfVisible()
    onVisibleChanged: loadDocumentsIfVisible()

    function loadDocumentsIfVisible() { if(visible) { documentsModel.load() } }
}

