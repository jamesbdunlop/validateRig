#  Copyright (c) 2019.  James Dunlop

import sys
import os
import logging
from PySide2 import QtWidgets, QtCore
from const import constants
from const import serialization as c_serialization
from core import inside
from core import validator as c_validator
from core import parser as c_parser
from uiStuff.themes import factory as uit_factory
from uiStuff.trees import factory as cuit_factory
from uiStuff.dialogs import saveToJSONFile as uid_saveToJSON
from uiStuff.dialogs import loadFromJSONFile as uid_loadFromJSON
from uiStuff.trees import validationTreeWidget as uit_validationTreeWidget
from uiStuff.dialogs import createValidator as uid_createValidator

logger = logging.getLogger(__name__)

# ToDo set stylesheet across all widgets


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
            []
        )  # list of tuples of validators and widgets (Validator, QTreeWidget)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setObjectName("mainLayout")

        self.subLayout01 = QtWidgets.QHBoxLayout()
        self.groupBoxesLayout = QtWidgets.QVBoxLayout()
        self.groupBoxesLayout.setObjectName("groupBoxLayout")

        # Buttons
        self.treeButtons = QtWidgets.QVBoxLayout()
        self.expandAll = QtWidgets.QPushButton("expand All")
        self.expandAll.clicked.connect(self.__expandAllTreeWidgets)
        self.collapseAll = QtWidgets.QPushButton("collapse All")
        self.collapseAll.clicked.connect(self.__collapseAllTreeWidgets)
        self.treeButtons.addWidget(self.expandAll)
        self.treeButtons.addWidget(self.collapseAll)
        self.treeButtons.addStretch(1)

        #
        self.applicationButtonLayout = QtWidgets.QHBoxLayout()
        self.newButton = QtWidgets.QPushButton("New")
        self.newButton.clicked.connect(self.__createValidatorNameInputDialog)

        self.loadButton = QtWidgets.QPushButton("Load")
        self.loadButton.clicked.connect(self.__loadDialog)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(self.__saveDialog)

        self.runButton = QtWidgets.QPushButton("Run")

        # Layout
        self.applicationButtonLayout.addWidget(self.newButton)
        self.applicationButtonLayout.addWidget(self.loadButton)
        self.applicationButtonLayout.addWidget(self.saveButton)
        self.treeButtons.addWidget(self.runButton)

        self.subLayout01.addLayout(self.groupBoxesLayout)
        self.subLayout01.addLayout(self.treeButtons)
        self.mainLayout.addLayout(self.applicationButtonLayout)
        self.mainLayout.addLayout(self.subLayout01)

        self.resize(1200, 800)

    def __expandAllTreeWidgets(self):
        for _, treeWidget in self._validators:
            treeWidget.expandAll()

    def __collapseAllTreeWidgets(self):
        for _, treeWidget in self._validators:
            treeWidget.collapseAll()

    # Create
    def __createValidationPair(self, data):
        """
        The (validator, treeWidget) tuple pair creator.

        :param data: `dict` result of a previously saved ValidationUI.toData()
        :type data: `dict`
        :return:
        """
        validatorName = data.get(c_serialization.KEY_VALIDATOR_NAME)
        if self.__findValidatorByName(validatorName) is not None:
            msg = "Validator named: `%s` already exists! Skipping!" % validatorName
            logger.warning(msg)
            raise Exception(msg)

        validator = self.__createValidatorFromData(data)
        treeWidget = self.__createValidationTreeWidget(validator=validator)
        self.runButton.clicked.connect(validator.validateSourceNodes)

        validatorpair = (validator, treeWidget)
        if validatorpair in self._validators:
            raise Exception(
                "Something bad happened! \nThe validation pair exists! But we didn't fail get_validatorbyName!"
            )

        self._validators.append((validator, treeWidget))
        return validator, treeWidget

    def __createValidatorFromData(self, data):
        """

        :type data: dict
        :return: `Validator`
        """
        validator = c_validator.getValidator(
            name=data.get(c_serialization.KEY_VALIDATOR_NAME, "")
        )

        return validator

    def __createValidationTreeWidget(self, validator):
        """Creates a treeView widget for the treeWidget/validator pair for adding source nodes to.
        :type validator: `c_validator.Validator`
        """
        treewidget = uit_validationTreeWidget.getValidationTreeWidget(validator, self)
        treewidget.remove.connect(self.__removeValidator)

        return treewidget

    def __addNewValidatorByName(self, name):
        """

        :type name: `str`
        """
        validator = c_validator.Validator(name=name)
        self.__addValidatorFromData(validator.toData())

    def __createValidatorNameInputDialog(self):
        self.nameInput = uid_createValidator.CreateValidatorDialog(
            title="Create Validator"
        )
        self.nameInput.setStyleSheet(
            uit_factory.getThemeData(self.theme, self.themeColor)
        )
        self.nameInput.name.connect(self.__addNewValidatorByName)
        self.nameInput.show()

    # Search
    def __findValidatorByName(self, name):
        """

        :type name: `str`
        :return: `c_validator.Validator`
        """
        for eachValidator in self.__iterValidators():
            if eachValidator.name == name:
                return eachValidator

    def __iterValidators(self):
        """

        :return: `c_validator.Validator`
        """
        for eachValidator, _ in self._validators:
            yield eachValidator

    # Dialogs
    def __saveDialog(self):
        """
        Writes to disk all the validation data for each validation treeWidget added to the UI.

        :return:
        """
        dialog = uid_saveToJSON.SaveJSONToFileDialog(parent=None)
        dialog.setStyleSheet(self.sheet)
        if dialog.exec_():
            for eachFile in dialog.selectedFiles():
                self.to_fileJSON(filepath=eachFile)

    def __loadDialog(self):
        dialog = uid_loadFromJSON.LoadFromJSONFileDialog(parent=None)
        dialog.setStyleSheet(self.sheet)
        if dialog.exec_():
            for filepath in dialog.selectedFiles():
                data = c_parser.read(filepath)
                if type(data) == list:  # We have a sessionSave from the UI of multiple validators
                    for validationData in data:
                        self.__addValidatorFromData(validationData, expanded=True)
                else:
                    self.__addValidatorFromData(data, expanded=True)

    # QT Drag and Drop
    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationUI, self).dragEnterEvent(QDragEnterEvent)
        return QDragEnterEvent.accept()

    def dropEvent(self, QDropEvent):
        super(ValidationUI, self).dropEvent(QDropEvent)
        if not inside.insideMaya() and QDropEvent.mimeData().text().endswith(".json"):
            self.processJSONDrop(QDropEvent)
        return QDropEvent.accept()

    def processJSONDrop(self, sender):
        data = c_parser.read(sender.mimeData().text().replace("file:///", ""))
        self.__addValidatorFromData(data)

    # App Create from
    def __addValidatorFromData(self, data, expanded):
        """
        Sets up a new validator/treeWidget for the validation data passed in.
        :param dict: of validation data

        :type data:`dict`
        :type expanded:`bool`
        :return:
        """
        validator, treeWidget = self.__createValidationPair(data)

        for sourceNodeData in data.get(c_serialization.KEY_VALIDATOR_NODES, list()):
            sourceNode = validator.addSourceNodeFromData(sourceNodeData)

            sourceNodeTreeWItm = cuit_factory.treeWidgetItemFromNode(node=sourceNode)
            treeWidget.addTopLevelItem(sourceNodeTreeWItm)

            for eachValidityNode in sourceNode.iterValidityNodes():
                treewidgetItem = cuit_factory.treeWidgetItemFromNode(eachValidityNode)
                sourceNodeTreeWItm.addChild(treewidgetItem)

            sourceNodeTreeWItm.setExpanded(expanded)
        groupBoxName = data.get(c_serialization.KEY_VALIDATOR_NAME, "None")
        self.__createValidationGroupBox(name=groupBoxName, treeWidget=treeWidget)

    def __createValidationGroupBox(self, name, treeWidget):
        """

        :type name: `str`
        :type treeWidget: `uit_validationTreeWidget.ValidationTreeWidget`
        :return: ` QtWidgets.QGroupBox`
        """
        # Validator GBox and treeWidget as child
        groupBox = QtWidgets.QGroupBox(name)
        groupBoxLayout = QtWidgets.QVBoxLayout(groupBox)
        groupBoxLayout.addWidget(treeWidget)
        self.groupBoxesLayout.addWidget(groupBox)

        return groupBox

    def __removeValidator(self, validatorList):
        """

        :param validatorList: [Validator, GroupBox]
        :type validatorList: `list` [Validator, GroupBox]
        """
        validator, groupBox = validatorList
        for eachValidator, treeWidget in self._validators:
            if validator.name == eachValidator.name:
                self._validators.remove((eachValidator, treeWidget))
                groupBox.setParent(None)
                del groupBox

    # Serialize
    def toData(self):
        """
        Collect all the validation data's into a list

        :return: `list` of validator dicts
        """
        validatorDataList = list()
        for eachValidator, _ in self._validators:
            validatorDataList.append(eachValidator.toData())

        return validatorDataList

    def to_fileJSON(self, filepath):
        """

        :param filepath: output path to validation.json file
        :type filepath: `str`
        :return: `bool`
        """
        data = self.toData()
        c_parser.write(filepath=filepath, data=data)

        return True

    @classmethod
    def from_fileJSON(cls, filepath, expanded=False, parent=None):
        """

        :param filepath: path to the a previous validation.json file
        :type filepath: `str`
        :return: `ValidationUI`
        """
        inst = cls(parent=parent)
        if not os.path.isfile(filepath):
            raise RuntimeError("%s is not valid!" % filepath)

        previousValidatorAppData = c_parser.read(filepath)

        # Handle loading from either a previously saved sessionList or a Validator.toData()
        if type(previousValidatorAppData) != list:
            previousValidatorAppData = [previousValidatorAppData]

        for eachValidatiorData in previousValidatorAppData:
            inst.__addValidatorFromData(data=eachValidatiorData, expanded=expanded)

        return inst


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv).instance()
    myWin = ValidationUI.from_fileJSON(
        filepath="T:/software/validateRig/tests/testValidator.json",
        expanded=True
    )
    # myWin = ValidationUI()
    myWin.show()
    sys.exit(app.exec_())
