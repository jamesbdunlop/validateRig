#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtWidgets


class LoadFromJSONFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadFromJSONFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*.json")
        self.setViewMode(QtWidgets.QFileDialog.Detail)
