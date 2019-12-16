from PySide2 import QtWidgets
from vrConst import constants as c_constants


class SaveJSONToFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(SaveJSONToFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*{}".format(c_constants.JSON_EXT))
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setViewMode(QtWidgets.QFileDialog.Detail)
