from __future__ import annotations
from serial.tools.list_ports_common import ListPortInfo
import sportident

import logging
import pprint
import time

import serial.tools.list_ports
from PySide6.QtCore import (
    QObject,
    QStringListModel,
    QThread,
    QTimer,
)
from sportident import SIReaderCardChanged, SIReaderException, SIReaderReadout

from .utils.grading import COURSES, InputData, ScoreType, SuccessStatus

logger = logging.getLogger(__name__)





class Backend:
    # this object should contain all the workers and logic

    def __init__(self, backend_interface, engine, enable_debug_console=False):
        # super().__init__()

        self.backend_interface = backend_interface
        self.engine = engine

        # create reader thread+worker, + wire it to the start signal
        self.reader_thread = QThread()
        self.reader_worker = ReaderWorker(engine, self)
        self.reader_worker.moveToThread(self.reader_thread)
        self.backend_interface.backend_started.connect(self.reader_worker.spin_thread)

        self.console_thread = QThread()
        if enable_debug_console:
            self.console_worker = DebugConsole(self)
            self.console_worker.moveToThread(self.console_thread)
            self.backend_interface.backend_started.connect(self.console_worker.console)

        # TODO: this code should live in QML
        # This should ideally be implemented by changing
        def hack_respond_to_readout(runner_grade):
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

        self.backend_interface.card_result_readout.connect(hack_respond_to_readout)

        def get_reader():
            logger.info(
                f"attempting to connect to port {self.backend_interface._selected_port}"
            )

            try:
                # discard the old reader if it exists
                if self.reader_worker.si_reader is not None:
                    self.reader_worker.si_reader.disconnect()
                    self.reader_worker.si_reader = None
                    self.backend_interface.set_port_connected(False)

                self.reader_worker.si_reader = SIReaderReadout(
                    self.backend_interface.selected_port_string
                )
                logger.info("connected!")

                self.backend_interface.set_port_connected(True)
            except SIReaderException:
                raise RuntimeError(
                    f"Could not open SI reader on port {self.backend_interface._selected_port}"
                )
        self.backend_interface.selectedPortChanged.connect(get_reader)

        # --- create our debug timer
        def update_time():
            # Pass the current time to QML.
            current_time = time.strftime("%H:%M:%S", time.localtime())
            self.backend_interface.set_time(current_time)

            self.backend_interface.set_ports(
                QStringListModel(
                    [port.device for port in serial.tools.list_ports.comports()]
                )
            )

        self.timer = QTimer(interval=500)  # msecs
        self.timer.timeout.connect(update_time)

    def start(self):
        self.timer.start()
        self.reader_thread.start()
        self.console_thread.start()

        self.backend_interface.backend_started.emit()

    def shutdown(self):
        self.reader_thread.terminate()
        self.console_thread.terminate()
        self.timer.stop()
        logger.info("threads safely stopped")

    def report_si_input(self, input_data: InputData):
        # when multiple courses are available, get_closest_course before grading
        best_guess_course = input_data.get_closest_course(COURSES)

        # runner_grade = input_data.score_against(best_guess_course, ScoreType( self.backend.backend_interface.scoringMode))
        runner_grade = input_data.score_against(
            best_guess_course, ScoreType(self.backend_interface._scoring_mode)
        )

        logger.info("Correctness: " + pprint.pformat(runner_grade.status))

        # Put stuff in the UI
        self.backend_interface.card_result_readout.emit(runner_grade)


class DebugConsole(QObject):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def console(self):
        backend = self.backend
        interface = self.backend.backend_interface

        from code import interact

        interact("DEBUG CONSOLE", local=locals())


class ReaderWorker(QObject):
    def __init__(self, engine, backend):
        super().__init__()
        self.engine = engine
        self.backend: Backend = backend

        self.si_is_ready = False
        self.si_reader = None

        logger.info("reader worker created")

    def spin_thread(self):
        logger.warning("starting si loop...")

        while True:
            if not self.si_is_ready:
                time.sleep(0.1)
                continue

            logger.info("starting instance of si loop...")
            # TODO: make port an argument or pull from the ui someplace

            try:
                # wait for poll
                while not self.si_reader.poll_sicard():
                    pass

                # process output
                self.backend.report_si_input(
                    InputData.from_si_result(self.si_reader.read_sicard())
                )
            except (SIReaderCardChanged, SIReaderException) as e:
                # this exception (card removed too early) can be ignored
                logger.warning(f"exception: {e}")

            # beep
            self.si_reader.ack_sicard()
