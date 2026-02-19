from __future__ import annotations

from hashlib import new
from sqlite3.dbapi2 import InterfaceError
import pprint
import time
import serial.tools.list_ports

# from fastlog import log
from sportident import SIReaderReadout, SIReaderCardChanged, SIReaderException

from PySide6.QtCore import QStringListModel, QTimer, QThread, QObject, QEnum, Signal,Slot,Property,PyClassProperty, QTimerEvent

from easysnec.utils.grading import COURSES, InputData, Grade, ScoreType, EMOJI_MAPPING

from enum import Enum
from functools import partial

# from warnings import DeprecationWarning

class BackendInterfacePython:
    pass

class DummyClass(QObject):
    @QEnum
    class BackendScoreType(Enum):
        SCORE_O = 1
        CLASSIC_O = 2
        ANIMAL_O = 3

class BackendInterface(QObject):
    # this object should contain all program state

    # https://www.qt.io/product/qt6/qml-book/ch19-python-build-app
    # https://wiki.qt.io/Qt_for_Python/Connecting_QML_Signals

    @QEnum
    class BackendScoreType(Enum):
        SCORE_O = 1
        CLASSIC_O = 2
        ANIMAL_O = 3

    # --- signals
    @Signal
    def backend_started(self): pass

    @Signal
    def score_scored(self, str): pass
    
    # --- logging slot
    @Slot(str)
    def log(self, string:str):
        # log.info(string)
        pass

    # ------------ QT properties
    # --- time property (rw) (this is our canary property)
    _time = "the time is now"
    def get_time(self):
        return self._time
    def set_time(self, new_time):
        if self._time != new_time:
            self._time = new_time
            self.timeChanged.emit(new_time)
    timeChanged = Signal(str)
    time = Property(str, get_time, set_time, notify=timeChanged) # ty: ignore[invalid-argument-type]
    

    # --- name property (rw)
    _name = 'name'
    def get_name(self):
        return self._name
    def set_name(self, new_name):
        if self._name != new_name:
            self._name = new_name
            self.nameChanged.emit(new_name)
    nameChanged = Signal(str)
    name = Property(str, get_name, set_name, notify=nameChanged) # ty: ignore[invalid-argument-type]


    # --- ports property (rw)
    _ports = QStringListModel([port.device for port in serial.tools.list_ports.comports()])
    def get_ports(self):
        return self._ports
    def set_ports(self, new_ports):
        if self._ports != new_ports:
            self._ports = new_ports
            self.portsChanged.emit(new_ports)
    portsChanged = Signal(QObject)
    ports = Property(QObject, get_ports, set_ports, notify=portsChanged) # ty: ignore[invalid-argument-type]


    # --- selected port property (rw)
    _selected_port = ""
    def get_selected_port(self):
        return self._selected_port
    def set_selected_port(self, new_selected_port):
        if self._selected_port != new_selected_port:
            self._selected_port = new_selected_port
            self.selectedPortChanged.emit(new_selected_port)
    selectedPortChanged = Signal(str)
    selectedPort = Property(str, get_selected_port, set_selected_port, notify=selectedPortChanged)  # ty: ignore[invalid-argument-type]

    
    # --- scoring mode property (rw)
    _scoring_mode = None
    def get_scoring_mode(self):
        return self._scoring_mode
    def set_scoring_mode(self, new_scoring_mode):
        if self._scoring_mode != new_scoring_mode:
            self._scoring_mode = new_scoring_mode
            self.scoringModeChanged.emit(new_scoring_mode)
    scoringModeChanged = Signal(str)
    scoringMode = Property(DummyClass.BackendScoreType, get_scoring_mode, set_scoring_mode, notify=scoringModeChanged)  # ty: ignore[invalid-argument-type]

    # --- course set property (rw)
    _course_set = ""
    def get_course_set(self):
        return self._course_set
    def set_course_set(self, new_course_set):
        if self._course_set != new_course_set:
            self._course_set = new_course_set
            self.courseSetChanged.emit(new_course_set)
    courseSetChanged = Signal(str)
    courseSet = Property(str, get_course_set, set_course_set, notify=courseSetChanged)  # ty: ignore[invalid-argument-type]


    # --- app_running property (rw)
    _running = False
    def get_running(self):
        return self._running
    def set_running(self, new_running):
        if self._running != new_running:
            self._running = new_running
            self.runningChanged.emit(new_running)
    runningChanged = Signal(str)
    running = Property(bool, get_running, set_running, notify=runningChanged)  # ty: ignore[invalid-argument-type]
    





class Backend:
    # this object should contain all the workers and logic

    def __init__(self, backend_interface, engine):
        # super().__init__()

        self.backend_interface = backend_interface
        
        # create reader thread+worker, + wire it to the start signal
        self.reader = QThread()
        self.reader_worker = self.ReaderWorker(engine)
        self.reader_worker.moveToThread(self.reader)
        self.backend_interface.backend_started.connect(self.reader_worker.spin_thread)


        # --- create our debug timer
        def update_time():
            # Pass the current time to QML.
            curr_time = time.strftime("%H:%M:%S", time.localtime())
            # write state to ui
            # self.backend_interface.time = curr_time
            self.backend_interface.set_time(curr_time)

        self.timer = QTimer(interval=100) # msecs 100 = 1/10th sec
        self.timer.timeout.connect(update_time)

        self.test_timer = QTimer(singleShot=True, interval=1000)
        self.test_timer.timeout.connect( partial(self.big_test, engine=engine) )

        # create our ports list
        def update_ports():
            curr_ports = QStringListModel([port.device for port in serial.tools.list_ports.comports()])
            self.backend_interface.set_ports(curr_ports)

        self.timer_ports = QTimer(interval=1000)
        self.timer_ports.timeout.connect(update_ports)
        
    def start(self):
        self.backend_interface.backend_started.emit()
        self.timer.start()
        self.test_timer.start()
        self.reader.start()

    def shutdown(self):
        self.reader.terminate()
        self.timer.stop()
        # log.success('threads safely stopped')

    def big_test(self, engine=None):
        # log.info('testing now!!')
        pass


    # --- nested classes
    class ReaderWorker(QObject):
        def __init__(self, engine):
            super().__init__()
            self.engine = engine

            # log.info('reader worker created')

        def get_reader(self):
            # TODO: retry
            # TODO: do not recreate each loop. cache once 
            for _ in range(10):
                try:
                    reader_port = BackendInterface.selectedPort
                    self.si = SIReaderReadout(reader_port)

                    # log.success(f'connected to SI at port {reader_port}')
                    return

                except:
                    time.sleep(1)
            raise RuntimeError("Could not open SI reader")

        def spin_thread(self):
            # log.info("starting si loop...")
            self.get_reader()
            
            while True:
                # log.info("starting instance of si loop...")
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
                    # log.warning(f'exception: {e}')
                    pass
                # beep
                self.si.ack_sicard()
                
                # when multiple courses are available, get_closest_course before grading
                best_guess_course = input_data.get_closest_course(COURSES)
                runner_grade = input_data.score_against(best_guess_course, BackendInterface.scoringMode)

                # Grade(input_data, best_guess_course, ScoreType.ANIMAL_O).score
                # log.info("Correctness: " + pprint.pformat(runner_correct))
                
                # Put stuff in the UI
                if runner_grade.status == SuccessStatus.SUCCESS:
                    self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-good-green.png')
                    self.engine.rootObjects()[0].setProperty('feedback_message', "")
                elif runner_grade.status == SuccessStatus.MISSES:
                    self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-bad.png')
                    self.engine.rootObjects()[0].setProperty('feedback_message', "Try again!")
                elif runner_grade.status == SuccessStatus.INCOMPLETE:
                    self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-surprised.png')
                self.engine.rootObjects()[0].setProperty('scoring_output', runner_grade.scoring_output)
