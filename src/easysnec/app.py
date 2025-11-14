import json
import pprint
import sys

from fastlog import log
from pathlib import Path
from sportident import SIReaderReadout, SIReaderCardChanged
from time import strftime, localtime

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QStringListModel, QUrl, QTimer, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .utils.grading import COURSES, InputData


class ReaderThread(QThread):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def run(self):
        log.success("running now")
        while True:
            log.info("polling now in loop")
            # TODO: make port an argument or pull from the ui someplace
            reader_port = '/dev/cu.SLAB_USBtoUART'


            try:
                # TODO: retry
                # TODO: do not recreate each loop. cache once
                si = SIReaderReadout(reader_port)

                # wait for poll
                while not si.poll_sicard():
                    pass

                # process output
                input_data = InputData.from_si_result(si.read_sicard())
            except SIReaderCardChanged:
                # this exception (card removed too early) can be ignored 
                pass

            # beep
            si.ack_sicard()
            
            # grade response
            # runner_correct = get_correctness_of_course(card_data, CURRENT_COURSE.stations)
            # runner_correct = input_data.score_against(CURRENT_COURSE)
            
            # when multiple courses are available, get_closest_course before grading
            best_guess_course = input_data.get_closest_course(COURSES)
            runner_correct = input_data.score_against(best_guess_course)

            log.debug("Correctness: " + pprint.pformat(runner_correct))
            
            # Put stuff in the UI
            if runner_correct:
                self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-good-green.png')
            else:
                self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-bad.png')


def main() -> None:
    # my_model = QStringListModel()
    # my_model.setStringList(data_list)

    # Set up the application window
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.load('./src/easysnec/qml/Main.qml')
    engine.quit.connect(app.quit)


    def update_time():
        # Pass the current time to QML.
        curr_time = strftime("%H:%M:%S", localtime())
        # write state to ui
        engine.rootObjects()[0].setProperty('currTime', curr_time)

    timer = QTimer()
    timer.setInterval(100)  # msecs 100 = 1/10th sec
    timer.timeout.connect(update_time)
    timer.start()
    
    reader_thread = ReaderThread(engine)
    reader_thread.start()

    # execute and cleanup
    app.exec()

if __name__ == '__main__':
    main()