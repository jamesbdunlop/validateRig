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
from uiStuff.dialogs import saveToJSONFile as uid_saveToJSON
from uiStuff.dialogs import loadFromJSONFile as uid_loadFromJSON
from uiStuff.trees import validationTreeWidget as uit_validationTreeWidget

logger = logging.getLogger(__name__)


class ValidationUI(QtWidgets.QWidget):
    def __init__(
        self, title=constants.UINAME, theme="core", themecolor="", parent=None
    ):
        super(ValidationUI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setObjectName("validator_mainWindow")
        self.setWindowFlags(QtCore.Qt.Window)
        self.theme = theme
        self.themeColor = themecolor
        self.sheet = uit_factory.getThemeData(self.theme, self.themeColor)
        self.setStyleSheet(self.sheet)
        self.setAcceptDrops(True)

        self._validators = (
            list()
        )  # list of tuples of validators and widgets (Validator, QTreeWidget)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setObjectName("mainLayout")

        self.groupBoxesLayout = QtWidgets.QVBoxLayout()
        self.groupBoxesLayout.setObjectName("groupBoxLayout")

        # Buttons
        self.treeButtons = QtWidgets.QHBoxLayout()
        self.expandAll = QtWidgets.QPushButton("expand All")
        self.expandAll.clicked.connect(self.__expandAll)
        self.collapseAll = QtWidgets.QPushButton("collapse All")
        self.collapseAll.clicked.connect(self.__collapseAll)
        self.treeButtons.addWidget(self.expandAll)
        self.treeButtons.addWidget(self.collapseAll)

        self.buttonLayout = QtWidgets.QHBoxLayout()

        self.loadButton = QtWidgets.QPushButton("Load")
        self.loadButton.clicked.connect(self._loadDialog)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(self._saveDialog)

        self.runButton = QtWidgets.QPushButton("Run")

        self.buttonLayout.addWidget(self.loadButton)
        self.buttonLayout.addWidget(self.saveButton)
        self.buttonLayout.addWidget(self.runButton)

        self.mainLayout.addLayout(self.treeButtons)
        self.mainLayout.addLayout(self.groupBoxesLayout)
        self.mainLayout.addLayout(self.buttonLayout)

        self.resize(1200, 800)

    def __expandAll(self):
        for _, treeWidget in self._validators:
            treeWidget.expandAll()

    def __collapseAll(self):
        for _, treeWidget in self._validators:
            treeWidget.collapseAll()

    # Create
    def createValidationPair(self, data):
        """
        The (validator, treeWidget) tuple pair creator.

        :param data: `dict` result of a previously saved ValidationUI.toData()
        :return:
        """
        validatorName = data.get(c_serialization.KEY_VALIDATOR_NAME)
        if self.findValidatorByName(validatorName) is not None:
            msg = "Validator named: `%s` already exists! Skipping!" % validatorName
            logger.warning(msg)
            raise Exception(msg)

        validator = self.createValidator(data)
        treeWidget = self.createValidationTreeWidget(validator=validator)
        validatorpair = (validator, treeWidget)
        if validatorpair in self._validators:
            raise Exception(
                "Something bad happened! \nThe validation pair exists! But we didn't fail get_validatorbyName!"
            )

        self._validators.append((validator, treeWidget))
        return validator, treeWidget

    def createValidator(self, data):
        """

        :param data: dict
        :return: `Validator`
        """
        return c_validator.Validator(
            name=data.get(c_serialization.KEY_VALIDATOR_NAME, "")
        )

    def createValidationTreeWidget(self, validator):
        """Creates a treeView widget for the treeWidget/validator pair for adding source nodes to.
        :param validator: `Validator`
        """
        if inside.insideMaya():
            treewidget = uit_validationTreeWidget.MayaValidationTreeWidget(
                validator, self
            )
        else:
            treewidget = uit_validationTreeWidget.ValidationTreeWidget(validator, self)

        treewidget.remove.connect(self.removeValidator)
        return treewidget

    # Search
    def findValidatorByName(self, name):
        """

        :param name: `str` shortName
        :return: `Validator`
        """
        for eachValidator in self.iterValidators():
            if eachValidator.name == name:
                return eachValidator

    def iterValidators(self):
        """

        :return: `Validator`
        """
        for eachValidator, _ in self._validators:
            yield eachValidator

    def toData(self):
        """
        Collect all the validation data's into a dict

        :return: `dict`
        """
        data = dict()
        for eachValidator, _ in self._validators:
            vd = eachValidator.toData()
            data[vd[c_serialization.KEY_VALIDATOR_NAME]] = vd

        return data

    # Dialogs
    def _saveDialog(self):
        """
        Writes to disk all the validation data for each validation treeWidget added to the UI.

        :return:
        """
        dialog = uid_saveToJSON.SaveJSONToFileDialog(parent=None)
        dialog.setStyleSheet(self.sheet)
        if dialog.exec_():
            for eachFile in dialog.selectedFiles():
                self.to_fileJSON(filepath=eachFile)

    def _loadDialog(self):
        # TODO make this a class like the save dialog
        dialog = uid_loadFromJSON.LoadFromJSONFileDialog(parent=None)
        dialog.setStyleSheet(self.sheet)
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
            node = validator.addSourceNodeFromData(sourceNodeData)

            # Create and add the treeWidgetItem to the treeWidget from the node
            sourceNodeTreeWItm = cuit_treewidgetitems.SourceNodeTreeWidgetItem(
                node=node
            )

            # Populate the rows with the validations for the node
            for eachChild in node.iterValidityNodes():
                if eachChild.nodeType == c_serialization.NT_DEFAULTVALUE:
                    treewidgetItem = cuit_treewidgetitems.DefaultValueTreeWidgetItem(
                        node=eachChild
                    )
                elif eachChild.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                    treewidgetItem = cuit_treewidgetitems.ConnectionTreeWidgetItem(
                        node=eachChild
                    )
                sourceNodeTreeWItm.addChild(treewidgetItem)

            sourceNodeTreeWItm.setExpanded(expanded)
            treeWidget.addTopLevelItem(sourceNodeTreeWItm)

        groupBoxName = data.get(c_serialization.KEY_VALIDATOR_NAME, "None")
        self.createValidationGroupBox(name=groupBoxName, treeWidget=treeWidget)

    def createValidationGroupBox(self, name, treeWidget):
        # Validator GBox and treeWidget as child
        groupBox = QtWidgets.QGroupBox(name)
        groupBoxLayout = QtWidgets.QVBoxLayout(groupBox)
        groupBoxLayout.addWidget(treeWidget)
        self.groupBoxesLayout.addWidget(groupBox)

        return groupBox

    def removeValidator(self, validatorList):
        """

        :param validatorList: `list` [Validator, GroupBox]
        """
        validator, groupBox = validatorList
        for eachValidator, treeWidget in self._validators:
            if validator.name == eachValidator.name:
                self._validators.remove((eachValidator, treeWidget))
                groupBox.setParent(None)
                del groupBox

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

    def to_fileJSON(self, filepath):
        """

        :param filepath: `str`
        :return:
        """
        data = self.toData()
        c_parser.write(filepath=filepath, data=data)

        return True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv).instance()
    myWin = ValidationUI.from_fileJSON(
        filepath="T:/software/validateRig/tests/validatorTestData.json"
    )
    # myWin = ValidationUI()
    myWin.show()
    sys.exit(app.exec_())
