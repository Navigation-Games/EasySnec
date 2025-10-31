import sys
import urllib.request
import json
from pathlib import Path

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QStringListModel, QUrl
from PySide6.QtGui import QGuiApplication


def main() -> None:

    # get our data
    url = "http://country.io/names.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))

    # Format and sort the data
    data_list = sorted(list(data.values()))

    # Set up the application window
    app = QGuiApplication(sys.argv)

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView) # ty: ignore[unresolved-attribute]

    # Expose the list to the Qml code
    my_model = QStringListModel()
    my_model.setStringList(data_list)
    view.setInitialProperties({"myModel": my_model})


    # Load the QML file
    view.setSource(QUrl.fromLocalFile('./src/easysnec/qml/Main.qml'))
    # Add the current directory to the import paths and load the main module.
    # view.engine().addImportPath(sys.path[0])
    # view.loadFromModule("App", "Main")

    # Show the window
    if view.status() == QQuickView.Error: # ty: ignore[unresolved-attribute]
        sys.exit(-1)
    view.show()

    # execute and cleanup
    app.exec()
    del view
