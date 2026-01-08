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

// https://doc.qt.io/archives/qt-5.15/qtquickcontrols2-customize.html#customizing-button


ApplicationWindow {
    id: root
    title: "EasySnec"



    // TODO: native menu bars
    // https://doc.qt.io/qt-6/qml-qtquick-controls-menubar.html

    // ------- Program State! TODO: Replace with a "Model" / big object that holds all the data
    // debug value
    property var currTime: '1'

    property bool connected: false
    property bool show_start_page: true

    // RESULTS
    property var image_path: "./resources/glassy-smiley-late.png"
    property var scoring_output: ""
    property var feedback_message: ""

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
                // Button {
                //     text: "open file"
                //     // onClicked: root.setIcon('./resources/navigation_games_logo_no_background.png')
                // }
                Button {
                    text: "settings / back to configuration"
                    onClicked: {
                        root.show_start_page = true;
                    }
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

                    color: root.dark_grey
                    text: backend.time
                    // text: root.currTime
                    // font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }
    }

    StackLayout {

        anchors.fill: parent
        currentIndex: root.show_start_page ? 0:1


        Pane { // setup pane
            id: setup_pane
            ColumnLayout {
                anchors.fill: parent

                Label {
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    text: root.connected ? "You're connected. Press START to begin" : "Connect reader and select port to get started"

                    color: "#5D5D5D"
                    font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                }


                RowLayout {
                    RowLayout {
                        Label {
                            text: "Course Set:"
                        }
                        ComboBox {
                            model: ["Builtins", "Load from File"]
                        }
                    }

                    RowLayout {
                        Label {
                            text: "Scoring Mode:"
                        }
                        ComboBox {
                            model: ["Score-O", "Animal-O"]
                        }
                    }

                    ComboBox {
                        textRole: "display"
                        model: backend.ports
                        background: Rectangle {
                            color: root.connected ? '#65c15a':'#a83434'
                        }
                    }

                    Button {
                        text: "Start"
                        // background: Rectangle {
                        //     color: root.ready ? '#65c15a':'#7b7b7b'
                        // }
                        onClicked: {
                            root.show_start_page = false;
                        }

                        // enabled: root.connected
                    }
                }
            }
        }

        Pane { // feedback pane
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
                    text: root.scoring_output
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
                    text: root.feedback_message
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
