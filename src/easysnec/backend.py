from sqlite3.dbapi2 import InterfaceError
import pprint
import time

from fastlog import log
from sportident import SIReaderReadout, SIReaderCardChanged, SIReaderException

from PySide6.QtCore import QStringListModel, QTimer, QThread, QObject, Signal,Slot,Property,PyClassProperty, QTimerEvent

from .utils.grading import COURSES, InputData, Grade, ScoreType

from functools import partial

# from warnings import DeprecationWarning

class BackendInterfacePython:
    pass

class BackendInterface(QObject):
    # this object should contain all program state

    # https://www.qt.io/product/qt6/qml-book/ch19-python-build-app
    # https://wiki.qt.io/Qt_for_Python/Connecting_QML_Signals

    # properties
    _ports = QStringListModel(['p1','p2','p3'])

    

    # --- signals
    @Signal
    def backend_started(self): pass
    
    # --- logging slot
    @Slot(str)
    def log(self, string:str):
        log.info(string)

    # ------------ QT properties
    # --- name property (r)
    _name = 'name'
    def get_name(self):
        return self._name
    def set_name(self, new_name):
        if self._name != new_name:
            self._name = new_name
            self.nameChanged.emit(new_name)

    nameChanged = Signal(str)
    name = Property(str, get_name, set_name, notify=nameChanged) # ty: ignore[invalid-argument-type]

    # --- test_property
    @Property(str)
    def test_value(self):
        return "this is a test value"
    @test_value.setter
    def set_test_value(self, new_test_value):
        log.warning('nice it worked')


    # --- ports property (r)
    def get_ports(self):
        return self._ports
    portsChanged = Signal(QObject)
    ports = Property(QObject, get_ports, notify=portsChanged) # ty: ignore[invalid-argument-type]

    # --- time property (rw)
    _time = "the time is now"
    timeChanged = Signal(str)
    def set_time(self, new_time):
        self._time = new_time
        self.timeChanged.emit(new_time)
    def get_time(self):
        return self._time
    time = Property(str, get_time, set_time, notify=timeChanged) # ty: ignore[invalid-argument-type]
    # @Property(str)
    # def time(self):
    #     return self._time
    # @time.setter
    # def set_time(self, new_time):
    #     self._time = new_time
    #     self.timeChanged.emit(new_time)

    

    # --- selected port property (rw)
    # --- port selected slot



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
        
    def start(self):
        self.backend_interface.backend_started.emit()
        self.timer.start()
        self.test_timer.start()
        self.reader.start()

    def shutdown(self):
        self.reader.terminate()
        self.timer.stop()
        log.success('threads safely stopped')

    def big_test(self, engine=None):
        log.info('testing now!!')
        pass


    # --- nested classes
    class ReaderWorker(QObject):
        def __init__(self, engine):
            super().__init__()
            self.engine = engine

            log.info('reader worker created')

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

        def spin_thread(self):
            log.info("starting si loop...")
            self.get_reader()
            
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
                    self.engine.rootObjects()[0].setProperty('scoring_output', "")
                    self.engine.rootObjects()[0].setProperty('runner_input', "")
                else:
                    self.engine.rootObjects()[0].setProperty('image_path', './resources/glassy-smiley-bad.png')
                    self.engine.rootObjects()[0].setProperty('scoring_output', "Correct course: " + ", ".join(best_guess_course.stations))
                    self.engine.rootObjects()[0].setProperty('runner_input', "Your attempt: " + ", ".join(input_data.stations))