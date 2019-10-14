
from PySide2 import QtWidgets


def insideMaya():
    activeWindow = QtWidgets.QApplication.activeWindow()

    if activeWindow is None:
        return False

    if activeWindow.objectName() == "MayaWindow":
        return True

    return False
