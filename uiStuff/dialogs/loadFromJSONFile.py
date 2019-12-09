from PySide2 import QtWidgets
from constants import constants as constants


class LoadFromJSONFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadFromJSONFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*{}".format(constants.JSON_EXT))
        self.setViewMode(QtWidgets.QFileDialog.Detail)
