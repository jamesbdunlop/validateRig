#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtWidgets, QtCore, QtGui

from validateRig.const import constants as vrconst_constants
from validateRig.const import serialization as vrc_serialization
from validateRig.core.nodes import Node

QTDISPLAYROLE = QtCore.Qt.DisplayRole


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        # type: (Node, *args, **kwargs) -> None
        super(TreeWidgetItem, self).__init__(*args, **kwargs)
        self._node = node
        self._reportStatus = node.status

        self.setColumnFontStyle()

    def node(self):
        return self._node

    def setNode(self, node):
        # type: (Node) -> None
        self._node = node

    def nodeType(self):
        return self.node().nodeType

    def updateDisplayName(self,):
        columnId = vrconst_constants.SRC_NODENAME_COLUMN
        qtRole = QTDISPLAYROLE
        value = self.node().displayName
        if self.nodeType() == vrc_serialization.NT_SOURCENODE:
            self.updateColumnData(columnId, qtRole, value)

        if self.nodeType() == vrc_serialization.NT_CONNECTIONVALIDITY:
            destNodeNameColId = vrconst_constants.DEST_NODENAME_COLUMN
            self.updateColumnData(destNodeNameColId, qtRole, value)

        for x in range(self.childCount()):
            childTWI = self.child(x)
            childTWI.updateDisplayName()

    def updateColumnData(self, columnId, qtRole, value):
        # type: (int, QtCore.Qt.DisplayRole, str) -> None
        self.setData(columnId, qtRole, value)

    def updateDefaultValue(self):
        qtRole = QTDISPLAYROLE
        if self.nodeType() == vrc_serialization.NT_DEFAULTVALUE:
            data = self.node().defaultValueData
            for _, dvValue in data.iteritems():
                valueColId = vrconst_constants.SRC_ATTRVALUE_COLUMN
                self.updateColumnData(valueColId, qtRole, dvValue)

    def updateConnectionSrcValue(self):
        qtRole = QTDISPLAYROLE
        if self.nodeType() == vrc_serialization.NT_CONNECTIONVALIDITY:
            data = self.node().connectionData
            srcData = data.get("srcData", None)
            value = srcData.get("attrValue")
            valueColId = vrconst_constants.SRC_ATTRVALUE_COLUMN
            self.updateColumnData(valueColId, qtRole, value)

    def setColumnFontStyle(self):
        font = QtGui.QFont("EA Font", weight=1)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        self.setFont(vrconst_constants.SRC_NODENAME_COLUMN, font)

        font2 = QtGui.QFont("EA Font", weight=1)
        font2.setBold(True)
        self.setFont(vrconst_constants.SRC_ATTR_COLUMN, font2)
        self.setFont(vrconst_constants.DEST_NODENAME_COLUMN, font2)

    def removeAllChildren(self):
        while self.childCount():
            for x in range(self.childCount()):
                self.removeChild(self.child(x))

    @property
    def children(self):
        children = [self.child(x) for x in range(self.childCount())]
        return children

    def iterDescendants(self):
        for c in self.children:
            yield c
            for c2 in c.children:
                yield c2

    @property
    def reportStatus(self):
        return self._reportStatus

    @reportStatus.setter
    def reportStatus(self, status):
        self._reportStatus = status
        self.updateColumnData(
            vrconst_constants.REPORTSTATUS_COLUMN, QtCore.Qt.DisplayRole, self._reportStatus
        )

        font2 = QtGui.QFont("EA Font", weight=1)
        font2.setBold(True)
        font2.setCapitalization(QtGui.QFont.AllUppercase)

        if self._reportStatus == vrconst_constants.NODE_VALIDATION_PASSED:
            self.setFont(vrconst_constants.REPORTSTATUS_COLUMN, font2)
        else:
            font2.setItalic(True)
            font2.setStrikeOut(True)
            self.setFont(vrconst_constants.REPORTSTATUS_COLUMN, font2)
