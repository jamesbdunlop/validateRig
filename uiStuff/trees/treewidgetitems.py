from PySide2 import QtWidgets, QtCore, QtGui
from constants import constants as cc_constants
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
    def reportStatus(self):
        return self._reportStatus

    @reportStatus.setter
    def reportStatus(self, status):
        self._reportStatus = status
        self.setData(cc_constants.REPORTSTATUS_COLUMN, QtCore.Qt.DisplayRole, status)
