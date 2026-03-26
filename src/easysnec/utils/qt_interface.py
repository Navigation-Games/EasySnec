from enum import Enum

from fastlog import log
from PySide6.QtCore import (
    QStringListModel,
    QObject,
    QEnum,
    Signal,
    Slot,
    Property,
)
import serial.tools.list_ports
from .grading import Grade


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
    backend_started = Signal()
    score_scored = Signal()
    try_connect_to_si_reader = Signal()
    card_result_readout = Signal(Grade)

    @Slot()
    def ping_port(self):
        log.info("pinging port")
        self.try_connect_to_si_reader.emit()

    # --- logging slot
    @Slot(str)
    def log(self, string: str):
        log.info(string)

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
    time = Property(str, get_time, set_time, notify=timeChanged)  # ty: ignore[invalid-argument-type]

    # --- name property (rw)
    _name = "name"

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        if self._name != new_name:
            self._name = new_name
            self.nameChanged.emit(new_name)

    nameChanged = Signal(str)
    name = Property(str, get_name, set_name, notify=nameChanged)  # ty: ignore[invalid-argument-type]

    # --- ports property (rw)
    _ports = QStringListModel(
        [port.device for port in serial.tools.list_ports.comports()]
    )

    def get_ports(self):
        return self._ports

    def set_ports(self, new_ports):
        if self._ports.stringList() != new_ports.stringList():
            self._ports = new_ports
            self.portsChanged.emit(new_ports)

    portsChanged = Signal(QObject)
    ports = Property(QObject, get_ports, set_ports, notify=portsChanged)  # ty: ignore[invalid-argument-type]

    # --- selected port property (rw)
    _selected_port = ""

    def get_selected_port(self):
        return self._selected_port

    def set_selected_port(self, new_selected_port):
        if self._selected_port != new_selected_port:
            self._selected_port = new_selected_port
            self.selectedPortChanged.emit(new_selected_port)

    selectedPortChanged = Signal(str)
    selectedPort = Property(
        str,
        get_selected_port,
        set_selected_port,
        notify=selectedPortChanged,  # ty: ignore[invalid-argument-type]
    )

    # --- scoring mode property (rw)
    _scoring_mode = 1

    def get_scoring_mode(self):
        return self._scoring_mode

    def set_scoring_mode(self, new_scoring_mode):
        if self._scoring_mode != new_scoring_mode:
            self._scoring_mode = new_scoring_mode
            self.scoringModeChanged.emit(new_scoring_mode)

    scoringModeChanged = Signal(str)
    scoringMode = Property(
        int,
        get_scoring_mode,
        set_scoring_mode,
        notify=scoringModeChanged,  # ty: ignore[invalid-argument-type]
    )

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
