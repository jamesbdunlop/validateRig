#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtWidgets
from const import constants as vrconst_constants


class SaveJSONToFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(SaveJSONToFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*{}".format(vrconst_constants.JSON_EXT))
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setViewMode(QtWidgets.QFileDialog.Detail)
