import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from core import validator as c_validator
from core.nodes import SourceNode, ValidityNode, DefaultNode
from core.ui.trees import treewidgetitems as cuit_treewidgetitems

# collapse ALL
# expand ALL
# QMainWindow with load save options
# search replace names? For namespaces? Or a nameSpace field?
# Validate buttons
# Shows errors. checkboxes? row colors?


class ValidationUI(QtWidgets.QWidget):
    def __init__(self, title='ValidationUI', parent=None):
        super(ValidationUI, self).__init__(parent=parent)
        self.setWindowTitle(title)
        self.setObjectName("validator_mainWindow")
        self.setAcceptDrops(True)

        # The base validator application
        self.validator = c_validator.Validator(name="Base Validator")

        # The main treeViewWidget for creating data
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.validatorTreeWidget = QtWidgets.QTreeWidget()
        self.validatorTreeWidget.setAcceptDrops(True)
        self.validatorTreeWidget.setColumnCount(7)
        self.validatorTreeWidget.setHeaderLabels(["SourceNodeName", "SrcAttrName", "SrcAttrValue",
                                                  "DestNodeName", "DestAttrName", "DestAttrValue",
                                                  "REPORT STATUS"])

        self.mainLayout.addWidget(self.validatorTreeWidget)

        self._setupTestUI()
        self.validatorTreeWidget.resizeColumnToContents(True)
        self.validatorTreeWidget.setAlternatingRowColors(True)

        # Temp buttons
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.load = QtWidgets.QPushButton("load")
        self.save = QtWidgets.QPushButton("save")
        self.run = QtWidgets.QPushButton("run")
        self.buttonLayout.addWidget(self.load)
        self.buttonLayout.addWidget(self.save)
        self.buttonLayout.addWidget(self.run)

        self.mainLayout.addLayout(self.buttonLayout)
        self.resize(800, 600)

    def _setupTestUI(self):
        """ Test data for working out UI / workflow """
        sn1 = SourceNode(name="master_ctrl")
        vdNode = ValidityNode(name="geo_hrc",
                              attributeName="showCloth", attributeValue=True,
                              srcAttributeName="visibility", srcAttributeValue=True)
        dvNode = DefaultNode(name="rotateOrder", defaultValue="xyz")
        sn1.addNodeToCheck(vdNode)
        sn1.addNodeToCheck(dvNode)
        sn2 = SourceNode(name="master_ctrl2")
        vdNode2 = ValidityNode(name="geo_hrc2",
                              attributeName="showCloth2", attributeValue=True,
                              srcAttributeName="visibility2", srcAttributeValue=True)
        dvNode2 = DefaultNode(name="rotateOrder2", defaultValue="xyz2")
        sn2.addNodeToCheck(vdNode2)
        sn2.addNodeToCheck(dvNode2)
        sourceNodes = [sn1, sn2]

        # Root source nodes
        for eachSourceNode in sourceNodes:
            self.validator.addNodeToValidate(eachSourceNode)

            w = cuit_treewidgetitems.SourceTreeWidgetItem(sourceNode=eachSourceNode)
            self.validatorTreeWidget.addTopLevelItem(w)

            # Populate the rows
            for eachChild in eachSourceNode.iterNodes():
                if isinstance(eachChild, ValidityNode):
                    ctw = cuit_treewidgetitems.ValidityTreeWidgetItem(validityNode=eachChild)
                    w.addChild(ctw)

                if isinstance(eachChild, DefaultNode):
                    dvtwi = cuit_treewidgetitems.DefaultTreeWidgetItem(defaultNode=eachChild)
                    dvtwi.reportStatus = "Failed"
                    w.addChild(dvtwi)

            w.setExpanded(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWin = ValidationUI(ValidationUI.__name__)
    myWin.show()
    app.exec_()
