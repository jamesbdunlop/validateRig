#  Copyright (c) 2019.  James Dunlop
import sys
import os
import logging
from PySide2 import QtWidgets, QtCore
from const import constants as vrc_constants
from const import serialization as c_serialization
from core import inside
from core import factory as c_factory
from core import validator as c_validator
from core import parser as c_parser
from uiElements.themes import factory as uit_factory
from uiElements.dialogs import saveToJSONFile as uid_saveToJSON
from uiElements.dialogs import loadFromJSONFile as uid_loadFromJSON
from uiElements.trees import validationTreeWidget as uit_validationTreeWidget
from uiElements.dialogs import createValidator as uid_createValidator

if inside.insideMaya():
    from maya import cmds

logger = logging.getLogger(__name__)


class ValidationUI(QtWidgets.QMainWindow):
    def __init__(
        self, title=vrc_constants.UINAME, theme="core", themecolor="", parent=None
    ):
        # type: (str, str, str, QtWidgets.QWidget) -> None
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

        # MAIN MENU
        self.appMenu = QtWidgets.QMenuBar()
        self.newButton = self.appMenu.addAction("New")
        self.newButton.triggered.connect(self.__createValidatorNameInputDialog)

        self.loadButton = self.appMenu.addAction("Load")
        self.loadButton.triggered.connect(self.__loadDialog)

        self.saveButton = self.appMenu.addAction("Save")
        self.saveButton.triggered.connect(self.__saveDialog)
        self.setMenuBar(self.appMenu)

        mainWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout(mainWidget)
        mainLayout.setObjectName("mainLayout")

        # CENTRAL WIDGET
        subLayout01 = QtWidgets.QVBoxLayout()
        self.groupBoxesLayout = QtWidgets.QVBoxLayout()
        self.groupBoxesLayout.setObjectName("groupBoxLayout")

        # Buttons
        self.treeButtons = QtWidgets.QHBoxLayout()
        self.expandAll = QtWidgets.QPushButton("expand All")
        self.expandAll.clicked.connect(self.__expandAllTreeWidgets)
        self.collapseAll = QtWidgets.QPushButton("collapse All")
        self.collapseAll.clicked.connect(self.__collapseAllTreeWidgets)

        self.showLongName = QtWidgets.QRadioButton("Show LongName")
        self.showLongName.setChecked(False)

        self.runButton = QtWidgets.QPushButton("Run")
        self.fixAllButton = QtWidgets.QPushButton("Fix All")
        self.fixAllButton.hide()

        self.isolateFailedButton = QtWidgets.QRadioButton("Isolate Failed")
        self.isolateFailedButton.setChecked(False)
        self.isolateFailedButton.toggled.connect(self.__toggleIsolateFailed)
        self.isolateFailedButton.setAutoExclusive(False)
        self.isolateFailedButton.hide()

        self.treeButtons.addWidget(self.expandAll)
        self.treeButtons.addWidget(self.collapseAll)
        self.treeButtons.addWidget(self.showLongName)
        self.treeButtons.addStretch(1)
        self.treeButtons.addWidget(self.runButton)
        self.treeButtons.addWidget(self.fixAllButton)
        self.treeButtons.addWidget(self.isolateFailedButton)

        self.inputsLayout = QtWidgets.QGridLayout()
        self.nameSpaceLabel = QtWidgets.QLabel("Namespace:")
        self.nameSpaceInput = QtWidgets.QLineEdit()
        self.nameSpaceInput.setPlaceholderText(
            "Will force a namespace across ALL valdiators."
        )
        self.nameSpaceInput.textChanged.connect(self.__updateValidatorsNameSpace)
        self.assignNamespaceButton = QtWidgets.QPushButton("From Selected")
        self.assignNamespaceButton.clicked.connect(self.__getNameSpaceFromScene)

        self.searchLabel = QtWidgets.QLabel("Search:")
        self.searchLabel.setFixedWidth(80)
        self.searchInput = QtWidgets.QLineEdit()
        self.searchInput.setPlaceholderText("Filter validationNodes by...")
        self.searchInput.textChanged.connect(self.__filterTreeWidgetItems)
        self.clearSearch = QtWidgets.QPushButton("Clear")
        self.clearSearch.clicked.connect(self.__clearSearch)
        self.clearSearch.setFixedWidth(150)

        self.inputsLayout.addWidget(self.nameSpaceLabel, 0, 0)
        self.inputsLayout.addWidget(self.nameSpaceInput, 0, 1)
        self.inputsLayout.addWidget(self.assignNamespaceButton, 0, 2)
        self.inputsLayout.addWidget(self.searchLabel, 1, 0)
        self.inputsLayout.addWidget(self.searchInput, 1, 1)
        self.inputsLayout.addWidget(self.clearSearch, 1, 2)

        # Layout
        subLayout01.addLayout(self.groupBoxesLayout)
        subLayout01.addLayout(self.treeButtons)
        mainLayout.addLayout(self.inputsLayout)
        mainLayout.addLayout(subLayout01)

        self.setCentralWidget(mainWidget)

        self.resize(1200, 800)

    # UI Manipulations
    def __filterTreeWidgetItems(self):
        searchString = self.searchInput.text()
        for eachValidationTreeWidget in self.__iterTreeWidgets():
            topLevelItems = list(eachValidationTreeWidget.iterTopLevelTreeWidgetItems())
            for treeWidgetItem in topLevelItems:
                node = treeWidgetItem.node()
                if searchString not in node.displayName:
                    treeWidgetItem.setHidden(True)
                else:
                    treeWidgetItem.setHidden(False)

                for x in range(treeWidgetItem.childCount()):
                    child = treeWidgetItem.child(x)
                    cNode = child.node()
                    if cNode.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                        if (
                            searchString not in cNode.name
                            and searchString not in cNode.srcAttrName
                            and searchString not in cNode.destAttrName
                        ):
                            child.setHidden(True)
                        else:
                            child.setHidden(False)
                            treeWidgetItem.setHidden(False)
                    elif cNode.nodeType == c_serialization.NT_DEFAULTVALUE:
                        if searchString not in cNode.name:
                            child.setHidden(True)
                        else:
                            child.setHidden(False)
                            treeWidgetItem.setHidden(False)

    def __clearSearch(self):
        self.searchInput.setText("")

    def __toggleFixAllButton(self):
        self.fixAllButton.hide()
        self.isolateFailedButton.hide()
        for eachValidator in self.__iterValidators():
            if eachValidator.failed:
                self.fixAllButton.show()
                self.isolateFailedButton.show()

    def __updateValidationStatus(self):
        treeWidgets = list(self.__iterTreeWidgets())

        # Iterthrough all the descendants of a SourceNode and if ANY of the children fail to pass validation set the
        # rootTreeWidgetItem to fail and the validation status to failed.
        for x, eachValidationTreeWidget in enumerate(treeWidgets):
            topLevelItems = list(eachValidationTreeWidget.iterTopLevelTreeWidgetItems())
            for treeWidgetItem in topLevelItems:
                sourceNodeStatus = list()
                for child in treeWidgetItem.iterDescendants():
                    status = child.node().status
                    child.reportStatus = status
                    sourceNodeStatus.append(
                        status == vrc_constants.NODE_VALIDATION_PASSED
                    )

                topLevelStatus = all(sourceNodeStatus)
                treeWidgetItem.reportStatus = vrc_constants.NODE_VALIDATION_FAILED
                if topLevelStatus:
                    treeWidgetItem.reportStatus = vrc_constants.NODE_VALIDATION_PASSED

        self.__toggleFixAllButton()

    def __updateValidatorsNameSpace(self):
        nameSpace = self.nameSpaceInput.text()
        for eachValidator in self.__iterValidators():
            eachValidator.nameSpace = nameSpace
            # eachValidator.updateNameSpaceInLongName()

            if not self.showLongName.isChecked():
                eachValidator._setAllNodeDisplayNamesToNamespaceShortName()

        self.__updateTreeWidgetDisplayNames()

    def __updateTreeWidgetDisplayNames(self):
        # Connected to via the signals from the validator if nameSpace or displayName change on the validator
        # in __addValidationPairFromData
        for eachValidationTreeWidget in self.__iterTreeWidgets():
            topLevelItems = list(eachValidationTreeWidget.iterTopLevelTreeWidgetItems())
            for treeWidgetItem in topLevelItems:
                treeWidgetItem.updateDisplayName()

                for x in range(treeWidgetItem.childCount()):
                    child = treeWidgetItem.child(x)
                    child.updateDisplayName()

            eachValidationTreeWidget.resizeColumnToContents(vrc_constants.SRC_NODENAME_COLUMN)
            eachValidationTreeWidget.resizeColumnToContents(vrc_constants.DEST_NODENAME_COLUMN)

    def __expandAllTreeWidgets(self):
        for _, treeWidget in self._validators:
            treeWidget.expandAll()

    def __collapseAllTreeWidgets(self):
        for _, treeWidget in self._validators:
            treeWidget.collapseAll()

    # UI Getters
    def __getNameSpaceFromScene(self):
        if inside.insideMaya():
            # Smelly find of NS from : in name.
            firstSelected = cmds.ls(sl=True)[0]
            if ":" in firstSelected:
                self.nameSpaceInput.setText(cmds.ls(sl=True)[0].split(":")[0])

        self.__updateValidatorsNameSpace()

    # UI Search
    def __findValidatorByName(self, name):
        # type: (str) -> c_validator.Validator

        for eachValidator in self.__iterValidators():
            if eachValidator.name == name:
                return eachValidator

    def __iterValidators(self):
        # type: () -> c_validator.Validator

        for eachValidator, _ in self._validators:
            yield eachValidator

    def __iterTreeWidgets(self):
        # type: () -> QtWidgets.QTreeWidget

        for _, treeWidget in self._validators:
            yield treeWidget

    def __toggleIsolateFailed(self, sender):
        treeWidgets = list(self.__iterTreeWidgets())
        for eachTWI in treeWidgets:
            topLevelItems = list(eachTWI.iterTopLevelTreeWidgetItems())
            for treeWidgetItem in topLevelItems:
                if not sender:
                    treeWidgetItem.setHidden(False)
                    continue

                if (
                    treeWidgetItem.node().status == vrc_constants.NODE_VALIDATION_PASSED
                    and sender
                ):
                    treeWidgetItem.setHidden(True)

    # UI Dialogs
    def __saveDialog(self):
        """Writes to disk all the validation data for each validation treeWidget added to the UI"""
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
                if (
                    type(data) == list
                ):  # We have a sessionSave from the UI of multiple validators
                    for validationData in data:
                        self.__addValidationPairFromData(validationData, expanded=True)
                else:
                    self.__addValidationPairFromData(data, expanded=True)

    # UI QT Drag and Drop
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
        self.__addValidationPairFromData(data)

    # App Creators
    def __createValidatorTreeWidgetPair(self, data):
        # type: (dict) -> tuple
        """The (validator, treeWidget) tuple pair creator."""

        validator = self.__createValidatorFromData(data)
        treeWidget = self.__createValidationTreeWidget(validator=validator)
        treeWidget.setStyleSheet(self.sheet)

        validatorpair = (validator, treeWidget)
        if validatorpair in self._validators:
            raise Exception(
                "Something bad happened! \nThe validation pair exists! But we didn't fail get_validatorbyName!"
            )

        self._validators.append(validatorpair)

        return validatorpair

    def __createValidatorFromData(self, data):
        # type: (dict) -> c_validator.Validator

        validatorName = data.get(c_serialization.KEY_VALIDATOR_NAME)
        if self.__findValidatorByName(validatorName) is not None:
            msg = "Validator named: `%s` already exists! Skipping!" % validatorName
            logger.warning(msg)
            raise Exception(msg)

        validator = c_factory.createValidator(
            name=data.get(c_serialization.KEY_VALIDATOR_NAME, ""), data=data
        )

        return validator

    def __createValidationTreeWidget(self, validator):
        # type: (c_validator.Validator) -> uit_validationTreeWidget.ValidationTreeWidget
        """Creates a treeView widget for the treeWidget/validator pair for adding source nodes to."""
        treewidget = uit_validationTreeWidget.getValidationTreeWidget(validator, self)
        treewidget.remove.connect(self.__removeValidatorFromUI)

        return treewidget

    def __createValidatorNameInputDialog(self):
        self.nameInput = uid_createValidator.CreateValidatorDialog(
            title="Create Validator"
        )
        self.nameInput.setStyleSheet(self.sheet)
        self.nameInput.name.connect(self.__createValidatorByName)
        self.nameInput.show()

    def __createValidatorByName(self, name):
        # type: (str) -> None
        validatorData = c_validator.Validator(name=name).toData()
        self.__addValidationPairFromData(data=validatorData)

    # App Create from
    def __addValidationPairFromData(self, data, expanded=False, depth=0):
        # type: (dict, bool) -> None
        """
        Sets up a new validator/treeWidget pair from the validation data and connects the validator to the global RUN button

        :param data: Validation data
        """
        validator, treeWidget = self.__createValidatorTreeWidgetPair(data)

        # Connect to main UI
        self.runButton.clicked.connect(validator.validateValidatorSourceNodes)
        self.runButton.clicked.connect(self.__updateValidationStatus)

        self.showLongName.toggled.connect(validator.toggleLongNodeNames)

        self.fixAllButton.clicked.connect(validator.repairValidatorSourceNodes)
        self.fixAllButton.clicked.connect(validator.validateValidatorSourceNodes)
        self.fixAllButton.clicked.connect(self.__updateValidationStatus)

        validator.displayNameChanged.connect(self.__updateTreeWidgetDisplayNames)

        groupBoxName = data.get(c_serialization.KEY_VALIDATOR_NAME, "None")
        self.__createValidationGroupBox(name=groupBoxName, treeWidget=treeWidget)

        if expanded:
            treeWidget.expandToDepth(depth)

    def __createValidationGroupBox(self, name, treeWidget):
        # type: (str, uit_validationTreeWidget.ValidationTreeWidget) -> QtWidgets.QGroupBox

        # Validator GBox and treeWidget as child
        groupBox = QtWidgets.QGroupBox(name)
        groupBoxLayout = QtWidgets.QVBoxLayout(groupBox)
        groupBoxLayout.addWidget(treeWidget)
        self.groupBoxesLayout.addWidget(groupBox)

        return groupBox

    def __removeValidatorFromUI(self, validatorList):
        # type: (list) -> None
        """:param validatorList: [Validator, GroupBox]"""
        validator, groupBox = validatorList
        for eachValidator, treeWidget in self._validators:
            if validator.name == eachValidator.name:
                self._validators.remove((eachValidator, treeWidget))
                groupBox.setParent(None)
                del groupBox

    # Serialize
    def toData(self):
        # type: () -> list
        """:return: Validator dictionaries"""
        validatorDataList = list()
        for eachValidator, _ in self._validators:
            validatorDataList.append(eachValidator.toData())

        return validatorDataList

    def to_fileJSON(self, filepath):
        # type: (str) -> bool
        """:param filepath: output path to validation.json file"""
        data = self.toData()
        c_parser.write(filepath=filepath, data=data)

        return True

    @classmethod
    def from_fileJSON(cls, filepath, expanded=False, parent=None):
        # type: (str, bool, QtWidgets) -> ValidationUI
        """
        :param filepath: path to the a previous validation.json file
        :param parent: QtWidget to parent to or None
        """
        inst = cls(parent=parent)
        if not os.path.isfile(filepath):
            raise RuntimeError("%s is not valid!" % filepath)

        previousValidatorAppData = c_parser.read(filepath)

        # Handle loading from either a previously saved sessionList or a Validator.toData()
        if type(previousValidatorAppData) != list:
            previousValidatorAppData = [previousValidatorAppData]

        for eachValidatiorData in previousValidatorAppData:
            inst.__addValidationPairFromData(data=eachValidatiorData, expanded=expanded)

        return inst


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv).instance()
    # myWin = ValidationUI.from_fileJSON(
    #     filepath="T:/software/validateRig/tests/testValidator.json", expanded=True
    # )
    myWin = ValidationUI.from_fileJSON(
        filepath="C:/temp/testMayaValidator.json", expanded=True
    )
    myWin.show()
    sys.exit(app.exec_())
