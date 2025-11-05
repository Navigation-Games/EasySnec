// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
// import QtCore 2.12


ApplicationWindow {
    visible: true
    width: 640
    height: 480
    property var myModel: '1234'
    property var currTime: '1'

    // header: Label {
    //     color: "#15af15"
    //     text: currTime
    //     font.pointSize: 17
    //     font.bold: true
    //     font.family: "Arial"
    //     renderType: Text.NativeRendering
    //     horizontalAlignment: Text.AlignHCenter
    //     padding: 10
    // }
    StackLayout {
        anchors.fill: parent
        
        Page {
            id: runPage

            ColumnLayout{
                anchors.fill: parent

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#ff0000"
                    Image {
                        id: image
                        fillMode: Image.PreserveAspectFit
                        // anchors.centerIn: root
                        anchors.fill:parent

                        source: "./resources/glassy-smiley-bad.png"
                    }
                }

                Label {
                    color: "#15af15"
                    text: "1234"
                    font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                    padding: 10

                    background: Rectangle {
                        anchors.fill: parent
                        color: "#333333"
                    }
                }
                Label {
                    color: "#15af15"
                    text: "567"
                    font.pointSize: 17
                    font.bold: true
                    font.family: "Arial"
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                    padding: 10
                }
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
