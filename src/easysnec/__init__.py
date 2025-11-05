# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QTextEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget)

import PySide6.QtAsyncio as QtAsyncio

import asyncio
import sys
import pprint
import serial.tools.list_ports

from sportident import SIReaderReadout

class MainWindow(QMainWindow):
    
    reader_port = ''
    CURRENT_COURSE = [31, 32, 33, 34, 35]

    def __init__(self):
        super().__init__()

        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        self.text = QLabel(f"Course: {self.CURRENT_COURSE}")
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignCenter)

        self.text = QLabel("Card Data: Unknown")
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignCenter)

        self.results = QLabel("Results: Unknown", textFormat=Qt.TextFormat.RichText)
        layout.addWidget(self.results, alignment=Qt.AlignmentFlag.AlignCenter)

        self.port_picker = QComboBox()
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        self.port_picker.addItems(ports)
        self.port_picker.currentTextChanged.connect(self.port_changed)

        layout.addWidget(self.port_picker)

        self.async_trigger = QPushButton(text="Poll for SI Card")
        self.async_trigger.clicked.connect(lambda: asyncio.ensure_future(self.read_card()))

        layout.addWidget(self.async_trigger, alignment=Qt.AlignmentFlag.AlignCenter)

    def port_changed(self, selected_port):
        print(f"port selected: {selected_port}")
        self.reader_port = selected_port

    async def wait_for_card_connection(self):
        si = SIReaderReadout(self.reader_port)
        while not si.poll_sicard():
            pass

        card_number = si.sicard
        card_type = si.cardtype

        # read out card data
        card_data = si.read_sicard()

        # beep
        si.ack_sicard()
        return { 'id': card_number, 'type': card_type, 'data': card_data }

    async def read_card(self):
        response = await self.wait_for_card_connection()
        self.text.setText(f"Card ID: {response['id']}\nCard Type: {response['type']}\nCard Data: {pprint.pformat(response['data'])}")
        print(pprint.pformat(response['data']))

        self.results.setText(self.get_runner_results(response['data'], self.CURRENT_COURSE))

    def get_runner_results(self, card_data, course_data):
        runner_punches = [ punch[0] for punch in card_data['punches'] ]
        result = f"<p>Your punches: {runner_punches}</p><p>Current course: {course_data}</p>"
        if course_data == runner_punches:
            result += f"<p><font color=\"green\">Great job!! :)</font></p>"
        else:
            result += f"<p><font color=\"red\">Oh no! There was a mistake :(</font></p>"
        return result

    def get_closest_course(self, card_data, courses):
        # fastDamerauLevenshtein
        # https://pypi.org/project/fastDamerauLevenshtein/#files
        s1 = [ punch[0] for punch in card_data['punches'] ]
        course_distances = {}

        for course in courses:
            s2 = course_data
            
            d: dict[tuple[int, int], int] = {}
            da: dict[T, int] = {}

            len1 = len(s1)
            len2 = len(s2)

            maxdist = len1 + len2
            d[-1, -1] = maxdist

            # matrix
            for i in range(len(s1) + 1):
                d[i, -1] = maxdist
                d[i, 0] = i
            for j in range(len(s2) + 1):
                d[-1, j] = maxdist
                d[0, j] = j

            for i, cs1 in enumerate(s1, start=1):
                db = 0
                for j, cs2 in enumerate(s2, start=1):
                    i1 = da.get(cs2, 0)
                    j1 = db
                    if self.test_func(cs1, cs2):
                        cost = 0
                        db = j
                    else:
                        cost = 1

                    d[i, j] = min(
                        d[i - 1, j - 1] + cost,     # substitution (wrong station)
                        d[i, j - 1] + 1,            # insertion (missed station)
                        d[i - 1, j] + 1,            # deletion (extra station)
                        d[i1 - 1, j1 - 1] + (i - i1) - 1 + (j - j1),  # transposition (swapped stations)
                    )

                da[cs1] = i

            course_distances[course] = d[len1, len2]

        return min(course_distances, key=course_distances.get)

    def get_correctness_of_course(self, card_data, course):
        # todo: make buffer array that helps display which stations are wrong compared to correct course 
        # See: triResultatsScore() and getMissed() in ResultatPuce.java from EasyGecNG
        correctness_array = []
        punches = [ punch[0] for punch in card_data['punches'] ]

        # temp solution
        for i in range(len(punches)):
            if course[i] == punches[i]:
                correctness_array.append(True)
            else:
                correctness_array.append(False)

            # buffer_string = ""
            # bufferBool = True
            # unsorted = True

            # while (unsorted):
            #     unsorted = False
            #     for i in range(len(punches)):
            #         if (punches[i] != punches[i + 1]):
            #             buffer_string = punches[i]
            #             punches[i] = punches[i + 1]
            #             punches[i + 1] = buffer_string
            #             unsorted = True
        
        return correctness_array

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    QtAsyncio.run(handle_sigint=True)
    
if __name__ == '__main__':
    main()