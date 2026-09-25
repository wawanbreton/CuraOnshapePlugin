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

    UM.I18nCatalog{id: catalog; name:"onshape"}

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

        ColumnLayout
        {
            anchors.fill: parent
            anchors.margins: UM.Theme.getSize("default_margin").width
            visible: documentsModel.loaded && !documentsModel.hasError
            spacing: UM.Theme.getSize("default_margin").height

            ColumnLayout
            {
                visible: documentsModel.hasConfigurationParameters
                Layout.fillWidth: true
                spacing: UM.Theme.getSize("narrow_margin").height

                UM.Label
                {
                    Layout.fillWidth: true
                    text: catalog.i18nc("@label", "Configurations")
                    font: UM.Theme.getFont("medium_bold")
                }

                Repeater
                {
                    model: documentsModel.configurationParameters

                    GridLayout
                    {
                        columns: 2
                        Layout.fillWidth: true
                        columnSpacing: UM.Theme.getSize("default_margin").width

                        UM.Label
                        {
                            Layout.preferredWidth: 140
                            Layout.alignment: Qt.AlignVCenter
                            text: modelData.name
                            font: UM.Theme.getFont("small")
                            elide: Text.ElideRight
                        }

                        Cura.ComboBox
                        {
                            Layout.fillWidth: true
                            Layout.maximumWidth: 280
                            model: modelData.options
                            textRole: "name"
                            currentIndex: modelData.selectedIndex
                            onActivated: modelData.selectedIndex = index
                        }
                    }
                }
            }

            ListView
            {
                id: listView
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: UM.Theme.getSize("default_margin").height
                model: documentsModel
                clip: true

                ScrollBar.vertical: UM.ScrollBar { id: verticalScrollBar }

                footer: LoadingItem
                {
                    width: listView.width
                    height: UM.Theme.getSize("card_icon").height * root.iconSizeFactor + 2 * UM.Theme.getSize("default_margin").height
                    visible: documentsModel.hasMorePages || documentsModel.isLoadingNextPage
                }

                delegate: DocumentCard { }

                onContentYChanged:
                {
                    // When the user scrolls close to the bottom, load the next page
                    var threshold = UM.Theme.getSize("card_icon").height * root.iconSizeFactor * 2
                    if (documentsModel.hasMorePages && !documentsModel.isLoadingNextPage &&
                        contentY + height >= contentHeight - threshold)
                    {
                        documentsModel.loadNextPage()
                    }
                }
            }
        }
    }

    Component.onCompleted: loadDocumentsIfVisible()
    onVisibleChanged: loadDocumentsIfVisible()

    StackView.onRemoved:
    {
        if(documentsModel.isSearchModel())
        {
            searchBar.clear();
        }
        destroy();
    }

    function loadDocumentsIfVisible() { if(visible) { documentsModel.load() } }
}

