import sys
import os
import logging
from PySide2 import QtWidgets, QtCore
from const import constants
from const import serialization as c_serialization
from core import inside
from core import validator as c_validator
from core import parser as c_parser
from core.nodes import SourceNode
from uiStuff.themes import factory as uit_factory
from uiStuff.trees import treewidgetitems as cuit_treewidgetitems
from uiStuff.dialogs import saveToJSONFile as uid_saveJSON
from uiStuff.trees import validationTreeWidget as uit_validationTreeWidget
logger = logging.getLogger(__name__)

"""
TEST MAYA USAGE:

import sys
paths = ["T:\\software\\validateRig", "C:\\Python27\\Lib\\site-packages"]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from shiboken2 import wrapInstance
from PySide2 import QtWidgets
def getMainWindowPtr(): 
    mayaMainWindowPtr = maya.OpenMayaUI.MQtUtil.mainWindow() 
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtWidgets.QMainWindow) 
    return mayaMainWindow
    
import app
reload(app)
from app import ValidationUI as vUI
myWin = vUI.from_fileJSON(filepath="T:/software/validateRig/core/tests/validatorTestData.json", 
                          parent=getMainWindowPtr())
myWin.show()

"""


class ValidationUI(QtWidgets.QWidget):
    def __init__(self, title=constants.UINAME, theme="core", themecolor="blue", parent=None):
        super(ValidationUI, self).__init__(parent=parent)
        """
        TO DO
        - collapse ALL
        - expand ALL
        - Search replace names? For namespaces? Or a nameSpace field?
        - Validate buttons
        - Shows errors. checkboxes? row colors?
        """
        self.setWindowTitle(title)
        self.setObjectName("validator_mainWindow")
        self.setWindowFlags(QtCore.Qt.Window)
        self.theme = theme
        self.themeColor = themecolor
        self.sheet = uit_factory.getThemeData(self.theme, self.themeColor)
        self.setStyleSheet(self.sheet)
        self.setAcceptDrops(True)

        self._validators = list()                   # list of tuples of validators and widgets (Validator, QTreeWidget)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setObjectName("mainLayout")

        self.treeWidgetLayout = QtWidgets.QVBoxLayout()
        self.treeWidgetLayout.setObjectName("widgetLayout")

        # Buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.loadButton = QtWidgets.QPushButton("Load")
        self.loadButton.clicked.connect(self._load)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(self._save)

        self.runButton = QtWidgets.QPushButton("Run")

        self.buttonLayout.addWidget(self.loadButton)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.runButton)

        self.mainLayout.addLayout(self.treeWidgetLayout)
        self.mainLayout.addLayout(self.buttonLayout)

        self.resize(1200, 800)

    # Create
    def createValidationPair(self, data):
        """
        The (validator, treeWidget) tuple pair creator.

        :param data: `dict` result of a previously saved ValidationUI.toData()
        :return:
        """
        validatorName = data.get(c_serialization.KEY_VALIDATOR_NAME)
        if self.validatorExistsByName(validatorName):
            msg = "Validator named: `%s` already exists! Skipping!" % validatorName
            logger.warning(msg)
            raise Exception(msg)

        validator = self.createValidator(data)
        treeWidget = self.createValidationTreeWidget(validator=validator)

        self._validators.append((validator, treeWidget))

        return validator, treeWidget

    def createValidator(self, data):
        return c_validator.Validator(name=data.get(c_serialization.KEY_VALIDATOR_NAME, ""))

    def createValidationTreeWidget(self, validator):
        """Creates a treeView widget for the treeWidget/validator pair for adding source nodes to.
        :param validator: `Validator`
        """
        if inside.insideMaya():
            return uit_validationTreeWidget.MayaValidationTreeWidget(validator, self)

        return uit_validationTreeWidget.ValidationTreeWidget(validator, self)

    # Search
    def findValidatorByName(self, name):
        for eachValidator in self.iterValidators():
            if eachValidator.name == name:
                return eachValidator

    def validatorExistsByName(self, name):
        """

        :param name:`str` name of the validator being added
        :return:
        """
        if self.findValidatorByName(name=name) is not None:
            return True

        return False

    def iterValidators(self):
        for eachValidator, _ in self._validators:
            yield eachValidator

    # Dialogs
    def _save(self):
        """
        Writes to disk all the validation data for each validation treeWidget added to the UI.

        :return:
        """
        # Collect all the validation data's
        data = dict()
        for eachValidator, _ in self._validators:
            vd = eachValidator.toData()
            data[vd[c_serialization.KEY_VALIDATOR_NAME]] = vd

        dialog = uid_saveJSON.SaveJSONToFileDialog(parent=None)
        dialog.setStyleSheet(self.sheet)
        if dialog.exec_():
            for eachFile in dialog.selectedFiles():
                c_parser.write(filepath=eachFile, data=data)

    def _load(self):
        # TODO make this a class like the save dialog
        dialog = QtWidgets.QFileDialog()
        dialog.setStyleSheet(self.sheet)
        dialog.setNameFilter("*{}".format(constants.JSON_EXT))
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if dialog.exec_():
            for filepath in dialog.selectedFiles():
                data = c_parser.read(filepath)
                for validatorName, validationData in data.items():
                    self.addValidatorFromData(validationData, expanded=True)

    # Drag and Drop
    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationUI, self).dragEnterEvent(QDragEnterEvent)
        return QDragEnterEvent.accept()

    def dropEvent(self, QDropEvent):
        super(ValidationUI, self).dropEvent(QDropEvent)
        return QDropEvent.accept()

    # App Create from
    def addValidatorFromData(self, data, expanded=False):
        """
        Sets up a new validator/treeWidget for the validation data passed in.

        :param data:`dict`
        :param expanded:`bool` To auto expand the results or not
        :return:
        """

        validator, treeWidget = self.createValidationPair(data)
        # Popuplate now
        for sourceNodeData in data.get(c_serialization.KEY_VALIDATOR_NODES, list()):
            # Create and add the validation node to the validator
            node = SourceNode.fromData(sourceNodeData)
            validator.addSourceNode(node)

            # Create and add the treeWidgetItem to the treeWidget from the node
            w = cuit_treewidgetitems.SourceTreeWidgetItem(node=node)

            # Populate the rows with the validations for the node
            for eachChild in node.iterValidityNodes():
                if eachChild.nodeType == c_serialization.NT_DEFAULTVALUE:
                    treewidgetItem = cuit_treewidgetitems.DefaultValueTreeWidgetItem(node=eachChild)
                else:
                    treewidgetItem = cuit_treewidgetitems.ConnectionValidityTreeWidgetItem(node=eachChild)
                w.addChild(treewidgetItem)

            w.setExpanded(expanded)
            treeWidget.addTopLevelItem(w)

        # Validator GBox and treeWidget as child
        groupBox = QtWidgets.QGroupBox(data.get(c_serialization.KEY_VALIDATOR_NAME, "None"))
        groupBoxLayout = QtWidgets.QVBoxLayout(groupBox)
        groupBoxLayout.addWidget(treeWidget)
        self.treeWidgetLayout.addWidget(groupBox)

        return validator, treeWidget

    @classmethod
    def from_fileJSON(cls, filepath, expanded=False, parent=None):
        """

        :param filepath: `str` path to the a previous validation.json file
        :return: `ValidationUI`
        """
        inst = cls(parent=parent)
        if not os.path.isfile(filepath):
            raise RuntimeError("%s is not valid!" % filepath)

        data = c_parser.read(filepath)
        for validatorName, validationData in data.items():
            inst.addValidatorFromData(data=validationData, expanded=expanded)

        return inst


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv).instance()
    myWin = ValidationUI.from_fileJSON(filepath="T:/software/validateRig/core/tests/validatorTestData.json")
    myWin.show()
    sys.exit(app.exec_())
