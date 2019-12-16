from PySide2 import QtWidgets, QtCore, QtGui
from vrConst import constants as cc_constants
from core.nodes import Node


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
        data = {
            cc_constants.REPORTSTATUS_COLUMN: (QtCore.Qt.DisplayRole, node.reportStatus)
        }

        self.updateData(data)

    def nodeType(self):
        return self.node().nodeType

    def updateData(self, data):
        # type: (dict) -> None
        for idx, value in data.items():
            self.setData(idx, value[0], value[1])

    def setColumnFontStyle(self):
        font = QtGui.QFont("EA Font", weight=1)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        self.setFont(cc_constants.SRC_NODENAME_COLUMN, font)

        font2 = QtGui.QFont("EA Font", weight=1)
        font2.setBold(True)
        self.setFont(cc_constants.SRC_ATTR_COLUMN, font2)
        self.setFont(cc_constants.DEST_NODENAME_COLUMN, font2)

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
        self.setData(cc_constants.REPORTSTATUS_COLUMN, QtCore.Qt.DisplayRole, status)
        font2 = QtGui.QFont("EA Font", weight=1)
        font2.setBold(True)
        font2.setCapitalization(QtGui.QFont.AllUppercase)

        if status == cc_constants.NODE_VALIDATION_PASSED:
            self.setFont(cc_constants.REPORTSTATUS_COLUMN, font2)
        else:
            font2.setItalic(True)
            font2.setStrikeOut(True)
            self.setFont(cc_constants.REPORTSTATUS_COLUMN, font2)

