from PySide2 import QtWidgets, QtCore
from const import constants as cc_constants

class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        super(TreeWidgetItem, self).__init__(*args, **kwargs)
        self._node = node
        self._reportStatus = node.status

    def node(self):
        return self._node

    def setNode(self, node):
        self._node = node
        data = {cc_constants.REPORTSTATUS_COLUMN: (QtCore.Qt.DisplayRole, node.reportStatus)}

        self.updateData(data)

    def nodeType(self):
        return self.node().nodeType

    def updateData(self, data):
        """

        :param data: `dict`
        :return: None
        """
        for idx, value in data.items():
            self.setData(idx, value[0], value[1])

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
