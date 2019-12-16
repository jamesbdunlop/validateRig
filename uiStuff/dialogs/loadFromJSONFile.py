from PySide2 import QtWidgets
from vrConst import constants as c_constants


class LoadFromJSONFileDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(LoadFromJSONFileDialog, self).__init__(parent=parent, *args, **kwargs)

        self.setNameFilter("*{}".format(c_constants.JSON_EXT))
        self.setViewMode(QtWidgets.QFileDialog.Detail)
