from __future__ import annotations
from pyapp.checks import Debug

import pprint
import time
import serial.tools.list_ports

from fastlog import log
from sportident import SIReaderReadout, SIReaderCardChanged, SIReaderException

from PySide6.QtCore import (
    QStringListModel,
    QTimer,
    QThread,
    QObject,
)

from .utils.grading import COURSES, InputData, SuccessStatus, ScoreType
from .utils.qt_interface import BackendInterface

from enum import Enum


class Backend:
    # this object should contain all the workers and logic

    def __init__(self, backend_interface, engine):
        # super().__init__()

        self.backend_interface = backend_interface

        # create reader thread+worker, + wire it to the start signal
        self.reader = QThread()
        self.reader_worker = ReaderWorker(engine, self)
        self.reader_worker.moveToThread(self.reader)
        self.backend_interface.backend_started.connect(self.reader_worker.spin_thread)


        self.console = QThread()
        self.console_worker = DebugConsole(self)
        self.console_worker.moveToThread(self.console)
        self.backend_interface.backend_started.connect(self.console_worker.console)


        def get_reader():
            log.info(f'attempting to connect to port {self.backend_interface._selected_port}')
            # TODO: retry
            for _ in range(10):
                try:
                    self.reader_worker.si_reader = SIReaderReadout(
                        self.backend_interface._selected_port
                    )
                    log.success("connected !")
                    self.reader_worker.si_is_ready = True
                    return
                except SIReaderException:
                    self.reader_worker.si_is_ready = False
                    time.sleep(0.1)
            raise RuntimeError("Could not open SI reader")

        self.backend_interface.try_connect_to_si_reader.connect(get_reader)

        # --- create our debug timer
        def update_time():
            # Pass the current time to QML.
            current_time = time.strftime("%H:%M:%S", time.localtime())
            self.backend_interface.set_time(current_time)

            old_port = self.backend_interface._selected_port
            current_ports = ['1','2','3','4'] # [port.device for port in serial.tools.list_ports.comports()]
            self.backend_interface.set_ports(QStringListModel(current_ports))
            
            if old_port in current_ports:
                self.backend_interface.set_selected_port(old_port)
            else:
                log.warning('selected port has disappeared! we must respond to this wisely')

        self.timer = QTimer(interval=00)  # msecs
        self.timer.timeout.connect(update_time)

    def start(self):
        self.timer.start()
        self.reader.start()
        self.console.start()
        self.backend_interface.backend_started.emit()

    def shutdown(self):
        self.reader.terminate()
        self.console.terminate()
        self.timer.stop()
        log.success("threads safely stopped")


    def report_si_input(self, input:InputData):
        # when multiple courses are available, get_closest_course before grading
        best_guess_course = input_data.get_closest_course(COURSES)
        
        # runner_grade = input_data.score_against(best_guess_course, ScoreType( self.backend.backend_interface.scoringMode))
        runner_grade = input_data.score_against(
            best_guess_course, ScoreType.ANIMAL_O
            # best_guess_course, BackendInterface.scoringMode
        )

        log.info("Correctness: " + pprint.pformat(runner_grade.status))

        # Put stuff in the UI
        if runner_grade.status == SuccessStatus.SUCCESS:
            self.engine.rootObjects()[0].setProperty(
                "image_path", "./resources/glassy-smiley-good-green.png"
            )
            self.engine.rootObjects()[0].setProperty("feedback_message", "")
        elif runner_grade.status == SuccessStatus.MISSES:
            self.engine.rootObjects()[0].setProperty(
                "image_path", "./resources/glassy-smiley-bad.png"
            )
            self.engine.rootObjects()[0].setProperty(
                "feedback_message", "Try again!"
            )
        elif runner_grade.status == SuccessStatus.INCOMPLETE:
            self.engine.rootObjects()[0].setProperty(
                "image_path", "./resources/glassy-smiley-surprised.png"
            )
        self.engine.rootObjects()[0].setProperty(
            "scoring_output", runner_grade.scoring_output
        )


class DebugConsole(QObject):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend


    def console(self):
        backend = self.backend
        interface = self.backend.backend_interface
        
        from code import interact
        interact('DEBUG CONSOLE', local=locals())

class ReaderWorker(QObject):
    def __init__(self, engine, backend):
        super().__init__()
        self.engine = engine
        self.backend:Backend = backend

        self.si_is_ready = False
        self.si_reader = None

        log.info("reader worker created")

    def spin_thread(self):
        log.warning("starting si loop...")

        while True:
            if not self.si_is_ready:
                time.sleep(0.1)
                continue

            log.info("starting instance of si loop...")
            # TODO: make port an argument or pull from the ui someplace

            try:
                # wait for poll
                while not self.si_reader.poll_sicard():
                    pass

                # process output
                self.backend.report_si_input(InputData.from_si_result(self.si_reader.read_sicard()))
            except (SIReaderCardChanged, SIReaderException) as e:
                # this exception (card removed too early) can be ignored
                log.warning(f"exception: {e}")

            # beep
            self.si_reader.ack_sicard()

            self.backend()
            
