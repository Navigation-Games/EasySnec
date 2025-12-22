from __future__ import annotations

import json
import pprint
import sys
import signal
import time
import random

from fastlog import log
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from .backend import BackendInterface, Backend


def main() -> None:
    # Set up the application window
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    
    # --- connect backend
    backend_interface = BackendInterface()
    context.setContextProperty('backend', backend_interface)
    backend = Backend(backend_interface, engine)
    backend.start()

    # TODO: This is prob how we embed files in the application
    # https://doc.qt.io/qtforpython-6/tutorials/basictutorial/qrcfiles.html
    engine.load('./src/easysnec/qml/Main.qml')
    if not engine.rootObjects():
        raise RuntimeError('QML Failed to load')
    
    # --- set app icon - this doesnt work yet lol
    # app.setWindowIcon(QIcon("./resources/navigation_games_logo_no_background.png"))

    # --- wire up qt to kill python and vice versa
    app.aboutToQuit.connect(backend.shutdown)
    signal.signal(signal.SIGINT, lambda x,y: app.quit())

    # --- start the app
    app.exec()


if __name__ == '__main__':
    main()