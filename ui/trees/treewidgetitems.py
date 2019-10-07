from PyQt5 import QtWidgets, QtCore
from core.nodes import ConnectionValidityNode, DefaultValueNode


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        super(TreeWidgetItem, self).__init__(*args, **kwargs)
        self._reportStatus = "--"
        self._node = node

    @property
    def reportStatus(self):
        return self._reportStatus

    @reportStatus.setter
    def reportStatus(self, status):
        self._reportStatus = status
        self.setData(6, QtCore.Qt.DisplayRole, status)


class SourceTreeWidgetItem(TreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        super(SourceTreeWidgetItem, self).__init__(node=node, *args, **kwargs)
        self.setData(0, QtCore.Qt.DisplayRole, self._node.name)
        self.setData(6, QtCore.Qt.DisplayRole, self.reportStatus)


class ValidityTreeWidgetItem(TreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        assert isinstance(node, ConnectionValidityNode), "validityNode is not an instance of ConnectionValidityNode!"
        super(ValidityTreeWidgetItem, self).__init__(node=node, *args, **kwargs)
        self.setData(1, QtCore.Qt.DisplayRole, self._node.attributeName)
        self.setData(2, QtCore.Qt.DisplayRole, self._node.attributeValue)
        self.setData(3, QtCore.Qt.DisplayRole, self._node.name)
        self.setData(4, QtCore.Qt.DisplayRole, self._node.srcAttributeName)
        self.setData(5, QtCore.Qt.DisplayRole, self._node.srcAttributeValue)
        self.setData(6, QtCore.Qt.DisplayRole, self.reportStatus)


class DefaultTreeWidgetItem(TreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        assert isinstance(node, DefaultValueNode), "defaultNode is not an instance of DefaultValueNode!"
        super(DefaultTreeWidgetItem, self).__init__(node=node, *args, **kwargs)
        self.setData(1, QtCore.Qt.DisplayRole, self._node.name)
        self.setData(2, QtCore.Qt.DisplayRole, str(self._node.defaultValue))
        self.setData(3, QtCore.Qt.DisplayRole, "----")
        self.setData(4, QtCore.Qt.DisplayRole, "----")
        self.setData(5, QtCore.Qt.DisplayRole, "----")
        self.setData(6, QtCore.Qt.DisplayRole, self.reportStatus)
