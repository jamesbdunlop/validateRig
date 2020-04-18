#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtWidgets


class SaveJSONToFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(SaveJSONToFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*.json")
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setViewMode(QtWidgets.QFileDialog.Detail)
