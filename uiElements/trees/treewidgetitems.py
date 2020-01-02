#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtWidgets, QtCore, QtGui
from const import constants as vrc_constants
from const import serialization as c_serialization
from core.nodes import Node
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
        columnId = vrc_constants.SRC_NODENAME_COLUMN
        qtRole = QTDISPLAYROLE
        value = self.node().displayName
        if self.nodeType() == c_serialization.NT_SOURCENODE:
            self.updateColumnData(columnId, qtRole, value)

        if self.nodeType() == c_serialization.NT_CONNECTIONVALIDITY:
            destNodeNameColId = vrc_constants.DEST_NODENAME_COLUMN
            self.updateColumnData(destNodeNameColId, qtRole, value)

        for x in range(self.childCount()):
            childTWI = self.child(x)
            childTWI.updateDisplayName()

    def updateColumnData(self, columnId, qtRole, value):
        # type: (int, QtCore.Qt.DisplayRole, str) -> None
        self.setData(columnId, qtRole, value)

    def setColumnFontStyle(self):
        font = QtGui.QFont("EA Font", weight=1)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        self.setFont(vrc_constants.SRC_NODENAME_COLUMN, font)

        font2 = QtGui.QFont("EA Font", weight=1)
        font2.setBold(True)
        self.setFont(vrc_constants.SRC_ATTR_COLUMN, font2)
        self.setFont(vrc_constants.DEST_NODENAME_COLUMN, font2)

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
        self.updateColumnData(vrc_constants.REPORTSTATUS_COLUMN, QtCore.Qt.DisplayRole, self._reportStatus)

        font2 = QtGui.QFont("EA Font", weight=1)
        font2.setBold(True)
        font2.setCapitalization(QtGui.QFont.AllUppercase)

        if self._reportStatus == vrc_constants.NODE_VALIDATION_PASSED:
            self.setFont(vrc_constants.REPORTSTATUS_COLUMN, font2)
        else:
            font2.setItalic(True)
            font2.setStrikeOut(True)
            self.setFont(vrc_constants.REPORTSTATUS_COLUMN, font2)
