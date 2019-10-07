import sys
import pprint
from PyQt5 import QtWidgets
from core import validator as c_validator
from core import parser as c_parser
from constants import constants
from constants import serialization as c_serialization
from core.nodes import SourceNode, ConnectionValidityNode, DefaultValueNode
from ui.trees import treewidgetitems as cuit_treewidgetitems
from ui.dialogs import saveToJSONFile as uid_saveJSON


class ValidationUI(QtWidgets.QWidget):
    def __init__(self, title='ValidationUI', parent=None):
        super(ValidationUI, self).__init__(parent=parent)
        # collapse ALL
        # expand ALL
        # Search replace names? For namespaces? Or a nameSpace field?
        # Validate buttons
        # Shows errors. checkboxes? row colors?

        self.setWindowTitle(title)
        self.setObjectName("validator_mainWindow")
        self.setAcceptDrops(True)

        # The base validator to be populated by drag and drop or a load
        self.validator = None

        # The main treeViewWidget for creating data
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.validatorTreeWidget = QtWidgets.QTreeWidget()
        self.validatorTreeWidget.setAcceptDrops(True)
        self.validatorTreeWidget.setColumnCount(7)
        self.validatorTreeWidget.setHeaderLabels(("SourceNodeName", "SrcAttrName", "SrcAttrValue",
                                                  "DestNodeName", "DestAttrName", "DestAttrValue",
                                                  "REPORT STATUS"))

        self.mainLayout.addWidget(self.validatorTreeWidget)

        self.__setupTestUI()
        self.validatorTreeWidget.resizeColumnToContents(True)
        self.validatorTreeWidget.setAlternatingRowColors(True)

        # Temp buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.load = QtWidgets.QPushButton("load")
        self.save = QtWidgets.QPushButton("save")
        self.save.clicked.connect(self._save)
        self.run = QtWidgets.QPushButton("run")
        self.buttonLayout.addWidget(self.load)
        self.buttonLayout.addWidget(self.save)
        self.buttonLayout.addWidget(self.run)

        self.mainLayout.addLayout(self.buttonLayout)
        self.resize(800, 600)

    def __setupTestUI(self):
        """ Test data for working out UI / workflow """
        testDataPath = "T:/software/validateRig/core/tests/validatorTestData.json"
        data = c_parser.read(testDataPath)
        self.validator = c_validator.Validator(name=data.get(c_serialization.KEY_VALIDATOR_NAME, "INVALID"))

        for sourceNodeData in data[c_serialization.KEY_VALIDATOR_NODES]:
            node = SourceNode.fromData(sourceNodeData)
            self.validator.addNodeToValidate(node)

            w = cuit_treewidgetitems.SourceTreeWidgetItem(node=node)
            self.validatorTreeWidget.addTopLevelItem(w)

            # Populate the rows
            for eachChild in node.iterNodes():
                if isinstance(eachChild, ConnectionValidityNode):
                    ctw = cuit_treewidgetitems.ValidityTreeWidgetItem(node=eachChild)
                    w.addChild(ctw)

                if isinstance(eachChild, DefaultValueNode):
                    dvtwi = cuit_treewidgetitems.DefaultTreeWidgetItem(node=eachChild)
                    dvtwi.reportStatus = "Failed"
                    w.addChild(dvtwi)

            w.setExpanded(True)

    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationUI, self).dragEnterEvent(QDragEnterEvent)
        dataAsText = QDragEnterEvent.mimeData().text()
        if dataAsText.endswith(constants.JSON_EXT):
            return QDragEnterEvent.accept()

    def dropEvent(self, QDropEvent):
        super(ValidationUI, self).dropEvent(QDropEvent)
        dataAsText = QDropEvent.mimeData().text()
        if dataAsText.endswith(constants.JSON_EXT):
            data = c_parser.read(dataAsText.replace("file:///", ""))
            pprint.pprint(data)

    def _save(self):
        dialog = uid_saveJSON.SaveJSONToFileDialog(parent=None)
        if dialog.exec():
            for eachFile in dialog.selectedFiles():
                c_parser.write(filepath=eachFile, data=self.validator.toData())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWin = ValidationUI(ValidationUI.__name__)
    myWin.show()
    app.exec_()
