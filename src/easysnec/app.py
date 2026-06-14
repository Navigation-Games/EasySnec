from __future__ import annotations
from serial.tools.list_ports_common import ListPortInfo
from typing import override, Protocol, Self, overload
import asyncio
from itertools import zip_longest
import logging
import time
import pprint
import random


import click
import slint
import slint.models
from sportident import SIReaderReadout, SIReaderException, SIReaderCardChanged
import serial.tools.list_ports

from easysnec.grading import InputData, COURSES, ScoreType, Grade, Course, SuccessStatus

logger = logging.getLogger(__name__)

from pathlib import Path

import playsound3



# Load the slint entry-points
try:
    loader = slint.loader.easysnec.ui

    AppWindow = loader.app_window.AppWindow
    MockWindow = loader.mock_window.MockSIController
    SlintGrade = loader.app_window.Grade
    SlintMistake = loader.app_window.Mistake
    SlintMistakeType = loader.app_window.MistakeType
    # SlintSIInputData = loader.app_window.SIInputData

except slint.CompileError as e:
    print(e.message)
    for d in e.diagnostics:
        print(d)
    print("could not compile!")
    quit(1)


def slint_grade_from_grade(grade: Grade):

    mistakes = [
        SlintMistake(
            checkpoint=c+1,
            type = SlintMistakeType.missed
        )
        for c in grade.missed_checkpoint_indices
    ]

    if not grade.input_data.start_time:
        mistakes.insert(0, SlintMistake(
            checkpoint=-1,
            type = SlintMistakeType.no_start
        ))
    if not grade.input_data.finish_time:
        mistakes.append(SlintMistake(
            checkpoint=-2,
            type = SlintMistakeType.no_finish
        ))


    if grade.status == SuccessStatus.SUCCESS:
        status = "success"
    if grade.status == SuccessStatus.INCOMPLETE:
        status = "incomplete"
    if grade.status == SuccessStatus.MISSES:
        status = "misses"

    if not grade.input_data.start_time or not grade.input_data.finish_time:
        time_text = ""
    else:
        time_delta = (grade.input_data.finish_time-grade.input_data.start_time)
        minutes = int(time_delta.seconds/60)
        seconds = time_delta.seconds%60
        time_text = f"{minutes:02}:{seconds:02}"

    return SlintGrade(
        course=grade.course.course_name,
        result=status,
        time=time_text,
        mistakes=slint.ListModel(mistakes)
    )

# def slint_input_from_input(input:InputData):

#     return SlintSIInputData (
#         card_id= int,
#         start_time= time.strftime("%H:%M:%S", input.start_time) if input.start_time else None,
#         finish_time= time.strftime("%H:%M:%S", input.finish_time),
#         punches= [int]
#     )


# define the connection to the main window
class App(AppWindow):
    # CONSTRUCTOR
    @classmethod
    def default(cls) -> Self:
        app = cls()

        app._serial_interface = ConcreteSerialInterface()

        app.request_update_ports()
        app.request_update_time()

        return app


    @classmethod
    def from_serial_interface(cls, serial_interface:SerialInterface) -> Self:
        app = cls.default()

        app._serial_interface = serial_interface

        app.request_update_ports()
        app.request_update_time()
        app.score_mode_options = slint.ListModel(['Animal-O']) # TODO: un-hardcode

        return app


    # PYTHON-ONLY STATE
    _si_reader: SIReaderReadout | MockSIReader | None = None
    _serial_interface: SerialInterface
    _input_data: InputData | None

    # CALLBACKS
    @slint.callback
    def request_decorative_button(self) -> None:
        print("you found the decorative button")

    @slint.callback
    def request_update_time(self) -> None:
        self.time = str(time.strftime("%H:%M:%S", time.localtime()))

    @slint.callback
    def request_update_ports(self) -> None:
        new_ports = self._serial_interface.get_port_list()

        old_ports = slint.models.ModelIterator(self.available_ports)

        # TODO: writing to properties always triggers updates in the system, even if nothing has changed. use getters/setters to do some equivalence checking?

        # if iter_not_the_same
        # NOTE: is it cleaner to do this with set equality?
        if any(map(lambda pair: pair[0] != pair[1], zip_longest(new_ports, old_ports))):
            # actually do an update
            self.available_ports = slint.ListModel(new_ports)

    @slint.callback
    def display_course(self, course) -> int:
        out = course.name + " "
        for checkpoint in course.checkpoints:
            out += str(int(checkpoint)) + " "
        return out

    @slint.callback
    def request_connect_si(self, port: str) -> None:
        print(f"trying to connect to port {port}...")
        try:
            if self._si_reader is not None:
                self._si_reader.disconnect()
                self._si_reader = None

            self._si_reader = self._serial_interface.bind_si_reader(port)
            self.si_connected = True
            print("success!")
        except SIReaderException:
            self.si_connected = False

    @slint.callback
    def request_check_si(self) -> None:
        logger.debug("checking the si reader...")

        if self._si_reader is None:
            return

        # TODO: This really might need to be async. won't know without hardware
        if not self._si_reader.poll_sicard():
            return

        try:
            self._input = InputData.from_si_result(self._si_reader.read_sicard())

            # beep
            self._si_reader.ack_sicard()

            courses = list(self._input.get_courses_sorted(COURSES))
            self.courses = slint.ListModel(map(lambda x: x.course_name, courses))

            best_guess_course = courses[0]

            self._report_output(self._input, best_guess_course)
            self._make_sound(self._input.score_against(best_guess_course))

        except (SIReaderCardChanged, SIReaderException) as e:
            # this exception (card removed too early) can be ignored
            logger.warning(f"exception: {e}")


    def _report_output(self, input:InputData, course:Course):
        print("grading si result...")

        runner_grade = input.score_against(
            course, ScoreType.ANIMAL_O # TODO: un-hardcode
        )

        logger.info("Correctness: " + pprint.pformat(runner_grade.status))

        # Put stuff in the UI
        slint_grade = slint_grade_from_grade(runner_grade)
        self.grade = slint_grade

        # import code
        # code.interact(local=locals(), local_exit=False)

    def _make_sound(self, grade:Grade):
        sound_path = Path(__file__).parent / 'ui' / 'resources' / 'sounds'
        if grade.status == SuccessStatus.SUCCESS:
            sound_path = sound_path / 'good'
        elif grade.status == SuccessStatus.INCOMPLETE:
            sound_path = sound_path / 'med'
        elif grade.status == SuccessStatus.MISSES:
            sound_path = sound_path / 'bad'

        all_sounds = list(sound_path.glob("*.mp3"))
        playsound3.playsound(random.choice(all_sounds), block=False)


    @slint.callback
    def request_regrade(self, course:str):
        course_obj = next(iter(filter(lambda x: x.course_name == course, COURSES)))
        self._report_output(self._input, course_obj)


    # UTILITY FUNCTIONS
    @slint.callback(global_name="Utils")
    def find(self, array: slint.ListModel, value: str) -> int:
        return array.list.index(value) if value in array.list else -1




# define a serial interface, that can be implemented by bare python or by the datastructure attached to the mock controller window
class SerialInterface(Protocol):
    def get_port_list(self) -> list[ListPortInfo]:
        ...
    def bind_si_reader(self, port:str) -> SIReaderReadout | MockSIReader:
        ...


# normal person serial interactions
class ConcreteSerialInterface(SerialInterface):
    @override
    def get_port_list(self) -> list[ListPortInfo]:
        return [port.device for port in serial.tools.list_ports.comports() ]

    @override
    def bind_si_reader(self, port:str) -> SIReaderReadout:
        return SIReaderReadout(port)

# crazy person serial interactions

class MockSIReader:
    insert_flag = False

    def poll_sicard(self) -> bool:
        if self.insert_flag:
            self.insert_flag = False
            return True
        # true on state changes, else false
        return False

    def read_sicard(self) -> dict:
        return {
            "card_number": 0,
            "start": 0,
            "finish": 0,
            "check": 0,
            "clear": 0,
            "punches": [(33, "1pm")],
        }

    def disconnect(self):
        pass  # noop

    def ack_sicard(self):
        print("beep!")
        pass  # noop


class MockWindowPy(MockWindow, SerialInterface):
    # serial interface protocol support
    mock_si_reader = MockSIReader()

    @override
    def get_port_list(self) -> list[ListPortInfo]:
        ports = [port.device for port in serial.tools.list_ports.comports() ]

        if self.si_reader_connection_status:
            ports.append(self.si_reader_port)

        return ports

    @override
    def bind_si_reader(self, port:str) -> SIReaderReadout | MockSIReader:
        if port != self.si_reader_port:
            raise SIReaderException()

        return self.mock_si_reader


    @slint.callback
    def si_card_inserted(self):
        print("inserted!")
        self.mock_si_reader.insert_flag = True



@click.command
@click.option("--mock", is_flag=True)
def main(mock: bool):
    logging.basicConfig(level=logging.INFO)


    if mock:
        serial_interface = MockWindowPy()
        serial_interface.show()
    else:
        serial_interface = ConcreteSerialInterface()

    app = App.from_serial_interface(serial_interface)
    app.show()

    # NOTE: you can also define a timer separate from / not owned by the app object
    # def mess_up_ports():
    #     print('messing up the ports')
    #     app.available_ports = slint.ListModel(['1', '/dev/ttyS3'])
    # debug_timer = slint.Timer()
    # debug_timer.single_shot(timedelta(seconds=1), mess_up_ports)

    # potentially: make a coroutine for polling the SI reader here
    async def main_receiver() -> None:
        result = await asyncio.sleep(0.5, result="hello")
        print(f"{result} from coroutine")

    slint.run_event_loop(main_receiver())
