#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtWidgets
from const import constants as vrc_constants


class LoadFromJSONFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadFromJSONFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*{}".format(vrc_constants.JSON_EXT))
        self.setViewMode(QtWidgets.QFileDialog.Detail)