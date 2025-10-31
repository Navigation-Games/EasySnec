import sys
import urllib.request
import json
from pathlib import Path

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QStringListModel, QUrl, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


def main() -> None:
    # Data nonsense we will not keep
    # TODO: Delete
    # get our data
    url = "http://country.io/names.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    # Format and sort the data
    data_list = sorted(list(data.values()))
    # Expose the list to the Qml code
    my_model = QStringListModel()
    my_model.setStringList(data_list)


    # Set up the application window
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"myModel": my_model})
    engine.load('./src/easysnec/qml/Main.qml')
    engine.quit.connect(app.quit)

    from time import strftime, localtime
    def update_time():
        # Pass the current time to QML.
        curr_time = strftime("%H:%M:%S", localtime())
        engine.rootObjects()[0].setProperty('currTime', curr_time)

    timer = QTimer()
    timer.setInterval(100)  # msecs 100 = 1/10th sec
    timer.timeout.connect(update_time)
    timer.start()

    # execute and cleanup
    app.exec()
