import sys
import os
import pprint
from PySide2 import QtWidgets, QtCore, QtGui
from uiStuff.themes import factory as uit_factory
from core import validator as c_validator
from core import parser as c_parser
from constants import constants
from constants import serialization as c_serialization
from core.nodes import SourceNode
from uiStuff.trees import treewidgetitems as cuit_treewidgetitems
from uiStuff.dialogs import saveToJSONFile as uid_saveJSON
from uiStuff.dialogs import attributeList as uid_attributeList
# import uiStuff.dialogs.attributeList as uid_attributeList
# reload(uid_attributeList)
from core import inside
"""
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
    def __init__(self, title=constants.UINAME, theme="core", themecolor="", parent=None):
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
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._appRCMenu)

    def _appRCMenu(self, point):
        menu = QtWidgets.QMenu()
        menu.addAction("AddSource")
        menu.exec_(self.mapToGlobal(point))

    def _TreeViewRCMenu(self, point):
        menu = QtWidgets.QMenu()
        menu.addAction("Fix")
        menu.exec_(self.mapToGlobal(point))

    def _createValidatorTreeWidget(self):
        # The main treeViewWidget for creating data
        widget = QtWidgets.QTreeWidget()
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(self._TreeViewRCMenu)
        widget.resizeColumnToContents(True)
        widget.setAcceptDrops(True)
        widget.setColumnCount(8)
        widget.setHeaderLabels(constants.HEADER_LABELS)

        self.treeWidgetLayout.addWidget(widget)

        return widget

    def _createValidationTuple(self, data):
        """

        :param data:`dict` Validation data
        :return:
        """
        self._validators.append((c_validator.Validator(name=data.get(c_serialization.KEY_VALIDATOR_NAME, "")),
                                 self._createValidatorTreeWidget()))

        return self._validators[-1]

    def _isValidFilepath(self, filepath):
        if not os.path.isfile(filepath):
            raise FileNotFoundError("%s" % filepath)

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

    def addValidatorFromData(self, data, expanded=False):
        """
        Sets up a new validator/treeWidget for the validation data passed in.

        :param data:`dict`
        :param expanded:`bool`  To auto expand the results or not
        :return:
        """
        validationTuple = self._createValidationTuple(data=data)

        # Popuplate now
        for sourceNodeData in data.get(c_serialization.KEY_VALIDATOR_NODES, list()):
            # Create and add the validation node to the validator
            node = SourceNode.fromData(sourceNodeData)
            validationTuple[0].addNodeToValidate(node)

            # Create and add the treeWidgetItem to the treeWidget from the node
            w = cuit_treewidgetitems.SourceTreeWidgetItem(node=node)
            validationTuple[1].addTopLevelItem(w)

            # Populate the rows with the validations for the node
            for eachChild in node.iterNodes():
                if eachChild.nodeType() == c_serialization.NT_CONNECTIONVALIDITY:
                    w.addChild(cuit_treewidgetitems.ValidityTreeWidgetItem(node=eachChild))

                if eachChild.nodeType() == c_serialization.NT_DEFAULTVALUE:
                    w.addChild(cuit_treewidgetitems.DefaultTreeWidgetItem(node=eachChild))

            w.setExpanded(expanded)

    ##### QT STUFF
    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationUI, self).dragEnterEvent(QDragEnterEvent)
        if inside.insideMaya():
            return QDragEnterEvent.accept()

        dataAsText = QDragEnterEvent.mimeData().text()
        if dataAsText.endswith(constants.JSON_EXT):
            return QDragEnterEvent.accept()

    def dropEvent(self, QDropEvent):
        super(ValidationUI, self).dropEvent(QDropEvent)
        dataAsText = QDropEvent.mimeData().text()
        if dataAsText.endswith(constants.JSON_EXT):
            data = c_parser.read(dataAsText.replace("file:///", ""))
            pprint.pprint(data)

        if inside.insideMaya():
            self.processMayaDrop(QDropEvent)

    def processMayaDrop(self, QDropEvent):
        """

        :param QDropEvent: `QDropEvent`
        :return:
        """
        # pop up the validity UI
        import maya.cmds as cmds
        data = QDropEvent.mimeData().text().split("\n")
        self.srcNodesWidget = uid_attributeList.SourceNodeAttributeListWidget(nodes=data,
                                                                              qParent=self)
        if self.srcNodesWidget is None:
            return

        self.srcNodesWidget.acceptButton.clicked.connect(self._accept)
        self.srcNodesWidget.move(QtGui.QCursor.pos())
        self.srcNodesWidget.resize(600, 900)
        self.srcNodesWidget.show()

    def _accept(self):
        self.srcNodesWidget.close()

    @classmethod
    def from_fileJSON(cls, filepath, parent=None):
        """

        :param filepath: `str` path to the a previous validation.json file
        :return: `ValidationUI`
        """
        inst = cls(parent=parent)
        inst._isValidFilepath(filepath)

        data = c_parser.read(filepath)
        for validatorName, validationData in data.items():
            inst.addValidatorFromData(validationData)

        return inst


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    myWin = ValidationUI.from_fileJSON(filepath="T:/software/validateRig/core/tests/validatorTestData.json")
    myWin.show()

    app.exec_()

