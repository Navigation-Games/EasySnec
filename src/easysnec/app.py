from __future__ import annotations

import argparse
import logging
import signal
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .backend import Backend
from .utils.qt_interface import BackendInterface

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug-console", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)


    # Set up the application window
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    context = engine.rootContext()

    # --- connect backend
    backend_interface = BackendInterface()
    context.setContextProperty("backend", backend_interface)
    backend = Backend(
        backend_interface, engine, enable_debug_console=args.debug_console
    )
    backend.start()

    # TODO: This is prob how we embed files in the application
    # https://doc.qt.io/qtforpython-6/tutorials/basictutorial/qrcfiles.html

    # In bundled builds, QML is placed next to the executable rather than
    # inside the package directory, so try both locations.
    file = Path(__file__).parent / "qml" / "Main.qml"
    if not file.exists():
        file = Path(sys.executable).parent / "qml" / "Main.qml"
    logger.info(f"loading qml from {file}")
    engine.load(file)
    if not engine.rootObjects():
        raise RuntimeError("QML Failed to load")

    # --- set app icon - this doesnt work yet lol
    # app.setWindowIcon(QIcon("./resources/navigation_games_logo_no_background.png"))

    # --- wire up qt to kill python and vice versa
    app.aboutToQuit.connect(backend.shutdown)
    signal.signal(signal.SIGINT, lambda x, y: app.quit())

    # --- start the app
    app.exec()
