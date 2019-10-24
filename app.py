import sys
import os
import pprint
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from const import constants
from const import serialization as c_serialization
from core import inside
from core import validator as c_validator
from core import parser as c_parser
from core.nodes import SourceNode
from uiStuff.themes import factory as uit_factory
from uiStuff.trees import treewidgetitems as cuit_treewidgetitems
from uiStuff.dialogs import saveToJSONFile as uid_saveJSON
from uiStuff.dialogs import attributeList as uid_attributeList
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

    def _removeItem(self, treeWidget, QPoint):
        treeWidget.itemAt(QPoint).parent().removeChild(treeWidget.itemAt(QPoint))

    def _removeAllItemsFromSourceNode(self, treeWidget, QPoint):
        treeWidget.itemAt(QPoint).removeAllChildren()

    def _removeALlSourceNodes(self, treeWidget):
        while treeWidget.topLevelItemCount():
            for x in range(treeWidget.topLevelItemCount()):
                treeWidget.takeTopLevelItem(x)

    def _createValidatorTreeWidget(self):
        # The main treeViewWidget for creating data
        widget = QtWidgets.QTreeWidget()
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(partial(self._TreeViewRCMenu, widget))
        widget.resizeColumnToContents(True)
        widget.setAcceptDrops(True)
        widget.setColumnCount(8)
        widget.setHeaderLabels(constants.HEADER_LABELS)

        self.treeWidgetLayout.addWidget(widget)

        return widget

    def _nodeTypeUnderCursor(self, treeWidget, QPoint):
        twi = treeWidget.itemAt(QPoint)
        if twi is None:
            return -1

        return twi.node().nodeType()

    def _TreeViewRCMenu(self, treeWidget, QPoint):
        menu = QtWidgets.QMenu()
        nodeType = self._nodeTypeUnderCursor(treeWidget, QPoint)
        if not nodeType:
            return

        # Test menu
        if nodeType == c_serialization.NT_SOURCENODE:
            removeAll = menu.addAction("remove All")
            removeAll.triggered.connect(partial(self._removeAllItemsFromSourceNode, treeWidget, QPoint))
        elif nodeType == c_serialization.NT_CONNECTIONVALIDITY or nodeType == c_serialization.NT_DEFAULTVALUE:
            remove = menu.addAction("remove validityNode")
            remove.triggered.connect(partial(self._removeItem, treeWidget, QPoint))
        else:
            menu.addAction("AddSource")
            clearAll = menu.addAction("clear All")
            clearAll.triggered.connect(partial(self._removeALlSourceNodes, treeWidget))

        menu.exec_(menu.mapToGlobal(QtGui.QCursor.pos()))

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
            raise RuntimeError("%s is not valid!" % filepath)

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
            for eachChild in node.iterValidityNodes():
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

    def iterValidators(self):
        for eachValidator, _ in self._validators:
            yield eachValidator

    def sourceNodeExists(self, nodeName):
        for validator in self.iterValidators():
            for srcNode in validator.iterSourceNodes():
                if srcNode.name == nodeName:
                    return srcNode

    def sourceNodeAttributeListWidget(self, sourceNodeName):
        """

        :param sourceNodeName: `str`
        :return: `SourceNodeAttributeListWidget` | `None`
        """
        existingSrcNode = self.sourceNodeExists(sourceNodeName.split("|")[-1])
        if existingSrcNode:
            return uid_attributeList.SourceNodeAttributeListWidget().fromSourceNode(sourceNode=existingSrcNode,
                                                                                    parent=self)

        return uid_attributeList.SourceNodeAttributeListWidget(nodeName=sourceNodeName, parent=self)

    def processMayaDrop(self, QDropEvent):
        """

        :param QDropEvent: `QDropEvent`
        :return:
        """
        if not inside.insideMaya():
            return

        import maya.cmds as cmds
        nodeNames = QDropEvent.mimeData().text().split("\n")

        # Check to see if this exists in the validator we dropped over.
        for nodeName in nodeNames:
            self.srcNodesWidget = self.sourceNodeAttributeListWidget(nodeName)
            if self.srcNodesWidget is None:
                continue

            self.srcNodesWidget.addSrcNodes.connect(self._accept)
            self.srcNodesWidget.move(QtGui.QCursor.pos())
            self.srcNodesWidget.resize(600, 900)
            self.srcNodesWidget.show()

    def _accept(self, srcDataList):
        """

        :param srcDataList: `list`
        :return: `None`
        """
        for srcNode in srcDataList:
            existing_srcNode = self.sourceNodeExists(srcNode.name)
            self._validators[-1][0].addNodeToValidate(srcNode, True)
            if not existing_srcNode:
                # Create and add the treeWidgetItem to the treeWidget from the node
                twi = cuit_treewidgetitems.SourceTreeWidgetItem(node=srcNode)
                self._validators[-1][1].addTopLevelItem(twi)

            else:
                # Find existing and remove them from the tree
                treeWidget = self._validators[-1][1]
                # Assuming only 1 ever exists!
                widgetList = treeWidget.findItems(existing_srcNode.name, QtCore.Qt.MatchExactly)
                if not widgetList:
                    continue

                twi = widgetList[0]
                for x in range(twi.childCount()):
                    twi.takeChild(x)

            # Populate the validation rows with validity nodes
            for eachVN in srcNode.iterValidityNodes():
                if eachVN.nodeType() == c_serialization.NT_CONNECTIONVALIDITY:
                    twi.addChild(cuit_treewidgetitems.ValidityTreeWidgetItem(node=eachVN))

                if eachVN.nodeType() == c_serialization.NT_DEFAULTVALUE:
                    twi.addChild(cuit_treewidgetitems.DefaultTreeWidgetItem(node=eachVN))

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
    app = QtWidgets.QApplication(sys.argv).instance()
    myWin = ValidationUI.from_fileJSON(filepath="T:/software/validateRig/core/tests/validatorTestData.json")
    myWin.show()
    sys.exit(app.exec_())
