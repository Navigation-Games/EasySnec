// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
// import QtQml

// docs
// https://doc.qt.io/qt-6/qml-tutorial2.html
// https://doc.qt.io/qt-6/qtcore-qmlmodule.html
// https://doc.qt.io/qt-6/qtqmlmodels-index.html

ApplicationWindow {
    id: root
    title: "EasySnec"



    // TODO: native menu bars
    // https://doc.qt.io/qt-6/qml-qtquick-controls-menubar.html

    // ------- Program State! TODO: Replace with a "Model" / big object that holds all the data
    // debug value
    property var currTime: '1'

    // all available ports (possibly filtered)
    property var portOptions: ["first", "second", "third"]
    // selected port (this is outgoing)
    property var currPort: 'test'

    property bool connected: false
    property bool show_start_page: false

    // RESULTS
    property bool result_status: false
    property var result_string: "You did it!" 

    property var image_path: "./resources/glassy-smiley-late.png"

    // ------- Program State!

    visible: true
    width: 640
    height: 480

    // colors!
    property var navgames_blue: "#0090f8" 
    property var navgames_orange: "#ff683a" 
    property var success_green: "#9AE99D" 
    property var info_blue: "#CBD9FF" 
    property var bad_red: "#FF9090"
    property var neutral_grey: "#DFDFDF" 
    property var dark_grey: "#B3B3B3" 

    header: Rectangle {
        // background
        width: parent.fillWidth
        // TODO: get this 20 from child margins.
        // TODO: actually this should be implicit and derived from chidren
        height: childrenRect.height + 20;
        color: root.neutral_grey

        RowLayout {

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            // anchors.bottom: parent.bottom

            anchors.leftMargin: 10
            anchors.rightMargin: 10
            anchors.topMargin: 10
            anchors.bottomMargin: 10

            height : buttons_group.implicitHeight
            // implicitHeight:40

            uniformCellSizes: true

            RowLayout {
                id: buttons_group
                Button {
                    text: "open file"
                    // onClicked: root.setIcon('./resources/navigation_games_logo_no_background.png')
                }
            }

            Rectangle {
                Layout.alignment: Qt.AlignHCenter 
                color: Qt.rgba(1, 0, 0, 0)
                Layout.fillHeight: true
                Layout.preferredWidth: 50 // TODO this should be implicit
                Image {
                    id: logo_image
                    fillMode: Image.PreserveAspectFit
                    // anchors.centerIn: root
                    anchors.fill:parent

                    source: "./resources/navigation_games_logo_no_background.png"
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight
                
                
                Label {

                    color: root.navgames_blue
                    text: root.currTime
                    // font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }
    }

    footer: Rectangle {
        // background
        // anchors.fill: parent
        width: parent.fillWidth
        height: childrenRect.height;
        color: root.neutral_grey
        
        RowLayout {
            // contents
            // spacing: 50
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: 10
            anchors.rightMargin: 10

            height: 50 //TODO: this should be implicit
            // anchors.topMargin: 10
            // anchors.bottomMargin: 10
            RowLayout {

                Label {
                    text: "Scoring Mode:"
                }
                ComboBox {
                    model: ["Score-O", "Animal-O"]
                }
            }

            RowLayout {
                id: usb_control_group
                Layout.alignment: Qt.AlignRight

                Label {
                    text: "Port Select: "
                }
                ComboBox {
                    // model: ["first", "second", "third"]
                    model: root.portOptions
                }

                Button {
                    text: "Connect"
                }

                Rectangle {
                    width: 15
                    height: width

                    color: root.connected ? root.success_green : root.bad_red
                    radius: width/2
                }

            }
        }

    }

    StackLayout {

        anchors.fill: parent
        currentIndex: root.show_start_page ? 0:1


        Pane {
            id: setup_pane
            ColumnLayout {
                anchors.fill: parent

                Label {
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    text: root.connected ? "You're connected" : "Connect reader to get started"

                    color: "#5D5D5D"
                    font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        Pane {
            id: feedback_pane
            ColumnLayout {
                anchors.fill: parent

                

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Qt.rgba(1, 0, 0, 0)
                    Image {
                        id: image
                        fillMode: Image.PreserveAspectFit
                        // anchors.centerIn: root
                        anchors.fill:parent

                        source: root.image_path
                    }
                }

                Label {
                    Layout.alignment: Qt.AlignHCenter

                    color: "#0090f8"
                    text: "1234"
                    font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                    padding: 10

                    // background: Rectangle {
                    //     anchors.fill: parent
                    //     // color: "#333333"
                    // }
                }
                Label {
                    Layout.alignment: Qt.AlignHCenter

                    color: "#0090f8"
                    text: "567"
                    font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                    padding: 10
                }
                // Label {
                //     color: "#15af15"
                //     // text: root.cardReading
                //     font.pointSize: 17
                //     font.bold: true
                //     font.family: "Arial"
                //     renderType: Text.NativeRendering
                //     horizontalAlignment: Text.AlignHCenter
                //     padding: 10
                // }
            }
        }
    }


    // what does this do?
    // NumberAnimation {
    //     id: anim
    //     running: true
    //     target: view
    //     property: "contentY"
    //     duration: 500
    // }
}
