from __future__ import annotations
from sportident import SIReaderReadout, SIReaderException, SIReaderCardChanged

from datetime import timedelta, datetime
import logging
import signal
import sys
import threading
import time
from pathlib import Path
from functools import partial
from dataclasses import dataclass
import pprint

import click
import slint
import serial.tools.list_ports

from .grading import InputData, COURSES, ScoreType

logger = logging.getLogger(__name__)


class App(slint.loader.easysnec.ui.app_window.AppWindow):
    @slint.callback
    def request_decorative_button(self) -> None:
        print('you found the decorative button')

    @slint.callback
    def request_update_time(self) -> None:
        self.time = str(time.strftime("%H:%M:%S", time.localtime()))

    @slint.callback
    def request_update_ports(self) -> None:
        self.available_ports = slint.ListModel([port.device for port in serial.tools.list_ports.comports()])

    @slint.callback
    def request_connect_si(self, port:str) -> None:
        print(f'trying to connect to port {port}...')
        try:
            if self._si_reader is not None:
                self._si_reader.disconnect()
                self._si_reader = None

            self._si_reader = SIReaderReadout(port)
            self.si_connected = True;
        except SIReaderException:
            self.si_connected = False;

    @slint.callback
    def request_check_si(self) -> None:
        print("checking the si reader...")

        # TODO: This really might need to be its own process or thread. won't know without hardware
        if not self._si_reader.poll_sicard(): return

        # process output
        try:
            input = InputData.from_si_result(self._si_reader.read_sicard())
            self._report_output(input)

            # beep
            self._si_reader.ack_sicard()
        except (SIReaderCardChanged, SIReaderException) as e:
            # this exception (card removed too early) can be ignored
            logger.warning(f"exception: {e}")


    def _report_output(self, input):
        print('grading si result...')

        best_guess_course = input.get_closest_course(COURSES)

        runner_grade = input.score_against(
            best_guess_course, ScoreType(self.backend_interface._scoring_mode)
        )

        logger.info("Correctness: " + pprint.pformat(runner_grade.status))

        # Put stuff in the UI
        runner_grade




    @classmethod
    def default(cls):
        app = cls()

        app.request_update_ports()
        app.request_update_time()

        app._si_reader = None

        # TODO: writing to properties always triggers updates in the system, even if nothing has changed. use getters/setters to do some equivalence checking?
        # NOTE: You can't write into structs, but you can create new ones and replace the reference
        # this will always trigger on-change events...
        # app.backend_state = slint.loader.easysnec.ui.app_window.BackendState(other_thing='whatrbsdfg');
        return app



# problem: slint hogs the GIL. solution: asyncio or processes, or write fast enough timer callbacks
# Use Python's asyncio library to write concurrent Python code with the async/await syntax.
# Slint's event loop is a full-featured asyncio event loop. While the event loop is running, asyncio.get_event_loop() returns a valid loop. To run an async function when starting the loop, pass a coroutine to slint.run_event_loop().


@click.command
@click.option('--mock', is_flag=True)
def main(mock:bool):
    logging.basicConfig(level=logging.INFO)

    app = App.default()
    app.run()

    # NOTE: you can also define a timer separate from / not owned by the app object
    # debug_timer = slint.Timer()
    # debug_timer.start(slint.TimerMode.Repeated, timedelta(seconds=0.5), partial(update_ports, app))
