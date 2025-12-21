import json
import pprint
import sys
import signal

from fastlog import log
from pathlib import Path
from sportident import SIReaderReadout, SIReaderCardChanged, SIReaderException
from time import strftime, localtime

# from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QStringListModel, QUrl, QTimer, QThread, Slot, QObject
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from .utils.grading import COURSES, InputData, Grade, ScoreType
import time


class ReaderThread(QThread):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        

    def get_reader(self):
        # TODO: retry
        # TODO: do not recreate each loop. cache once
        for _ in range(10):
            try:
                reader_port = 'COM5'
                self.si = SIReaderReadout(reader_port)

                log.success(f'connected to SI at port {reader_port}')
                return

            except:
                time.sleep(1)
        raise RuntimeError("Could not open SI reader")


    def run(self):
        self.get_reader()
        
        log.info("starting si loop...")
        while True:
            log.info("starting instance of si loop...")
            # TODO: make port an argument or pull from the ui someplace
            # reader_port = '/dev/cu.SLAB_USBtoUART'

            try:
                # wait for poll
                while not self.si.poll_sicard():
                    pass

                # process output
                input_data = InputData.from_si_result(self.si.read_sicard())
            except (SIReaderCardChanged, SIReaderException) as e:
                # this exception (card removed too early) can be ignored 
                log.warning(f'exception: {e}')

            # beep
            self.si.ack_sicard()
            
            # grade response
            # runner_correct = get_correctness_of_course(card_data, CURRENT_COURSE.stations)
            # runner_correct = input_data.score_against(CURRENT_COURSE)
            
            # when multiple courses are available, get_closest_course before grading
            best_guess_course = input_data.get_closest_course(COURSES)
            runner_correct = input_data.score_against(best_guess_course)

            # Grade(input_data, best_guess_course, ScoreType.ANIMAL_O).score
            log.info("Correctness: " + pprint.pformat(runner_correct))
            
            # Put stuff in the UI
            if runner_correct:
                self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-good-green.png')
            else:
                self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-bad.png')


# https://wiki.qt.io/Qt_for_Python/Connecting_QML_Signals
class Console(QObject):
    @Slot(str)
    def outputStr(self, s):
        print(s)

def main() -> None:
    # my_model = QStringListModel()
    # my_model.setStringList(data_list)

    # Set up the application window
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    # TODO: This is prob how we embed files in the application
    # https://doc.qt.io/qtforpython-6/tutorials/basictutorial/qrcfiles.html
    engine.load('./src/easysnec/qml/Main.qml')

    con = Console()
    context = engine.rootContext()
    context.setContextProperty('cont_2', con)
    engine.rootObjects()[0].setProperty('con', con)
    
    # wire up qt to kill python and vice versa
    engine.quit.connect(app.quit)
    signal.signal(signal.SIGINT, lambda x,y: app.quit())

    # window = QMainWindow()
    # window.setWindowTitle("Codeloop.org")
 
    # icon = QIcon("qt.png")
    # window.setWindowIcon(icon)
    # window.setWindowIcon(QIcon("./resources/navigation_games_logo_no_background.png"))

    # engine.rootObjects()[0].setIcon(QIcon("./resources/navigation_games_logo_no_background.png"))
    app.setWindowIcon(QIcon("./resources/navigation_games_logo_no_background.png"))


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
    # TODO: if this thread crashes, it should stop the program!!!
    
    
    # execute and cleanup
    app.exec()


if __name__ == '__main__':
    main()