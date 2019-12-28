#  Copyright (c) 2019.  James Dunlop

from PySide2 import QtWidgets, QtCore


class CreateValidatorDialog(QtWidgets.QInputDialog):
    name = QtCore.Signal(str, name="name")

    def __init__(self, title, parent=None, *args, **kwargs):
        # type: (str, QtWidgets.QWidget, *args, **kwargs) -> None
        super(CreateValidatorDialog, self).__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle(title)
        self.setLabelText("Validator Name: ")

    def done(self, result):
        # type: (int) -> None
        self.name.emit(self.textValue())
        super(CreateValidatorDialog, self).done(result)
