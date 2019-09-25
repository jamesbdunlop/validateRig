from PyQt5 import QtWidgets, QtCore
from core.nodes import ValidityNode, DefaultNode


class SourceTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, sourceNode):
        super(SourceTreeWidgetItem, self).__init__()
        self._sourceNode = sourceNode
        self._reportStatus = "NA"

        self.setData(0, QtCore.Qt.DisplayRole, self._sourceNode.name)
        self.setData(6, QtCore.Qt.DisplayRole, self.reportStatus)

    @property
    def reportStatus(self):
        return self._reportStatus

    @reportStatus.setter
    def reportStatus(self, status):
        self._reportStatus = status
        self.setData(6, QtCore.Qt.DisplayRole, status)


class ValidityTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, validityNode):
        super(ValidityTreeWidgetItem, self).__init__()
        assert isinstance(validityNode, ValidityNode), "validityNode is not an instance of ValidityNode!"
        self._validityNode = validityNode
        self._reportStatus = "NA"

        self.setData(1, QtCore.Qt.DisplayRole, self._validityNode.attributeName)
        self.setData(2, QtCore.Qt.DisplayRole, self._validityNode.attributeValue)
        self.setData(3, QtCore.Qt.DisplayRole, self._validityNode.name)
        self.setData(4, QtCore.Qt.DisplayRole, self._validityNode.srcAttributeName)
        self.setData(5, QtCore.Qt.DisplayRole, self._validityNode.srcAttributeValue)
        self.setData(6, QtCore.Qt.DisplayRole, self.reportStatus)

    @property
    def reportStatus(self):
        return self._reportStatus

    @reportStatus.setter
    def reportStatus(self, status):
        self._reportStatus = status
        self.setData(6, QtCore.Qt.DisplayRole, status)


class DefaultTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, defaultNode):
        super(DefaultTreeWidgetItem, self).__init__()
        assert isinstance(defaultNode, DefaultNode), "defaultNode is not an instance of DefaultNode!"
        self._defaultNode = defaultNode
        self._reportStatus = "NA"

        self.setData(1, QtCore.Qt.DisplayRole, self._defaultNode.name)
        self.setData(2, QtCore.Qt.DisplayRole, self._defaultNode.defaultValue)
        self.setData(6, QtCore.Qt.DisplayRole, self.reportStatus)

    @property
    def reportStatus(self):
        return self._reportStatus

    @reportStatus.setter
    def reportStatus(self, status):
        self._reportStatus = status
        self.setData(6, QtCore.Qt.DisplayRole, status)
