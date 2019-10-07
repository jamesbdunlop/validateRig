from PyQt5 import QtWidgets
from constants import constants as constants


class SaveJSONToFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(SaveJSONToFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*{}".format(constants.JSON_EXT))
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setViewMode(QtWidgets.QFileDialog.Detail)
