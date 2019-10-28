from PySide2 import QtWidgets, QtCore, QtGui
from core.nodes import ConnectionValidityNode, DefaultValueNode
from const import constants as constants
from uiStuff.themes import factory as cui_theme


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        super(TreeWidgetItem, self).__init__(*args, **kwargs)
        self._reportStatus = constants.DEFAULT_REPORTSTATUS
        self._node = node

    def node(self):
        return self._node

    def setNode(self, node):
        self._node = node
        self.updateData()

    def nodeType(self):
        return self.node().nodeType

    def updateData(self):
        pass

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
        self.setData(7, QtCore.Qt.DisplayRole, status)


class SourceTreeWidgetItem(TreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        super(SourceTreeWidgetItem, self).__init__(node=node, *args, **kwargs)
        for x in range(7):
            self.setBackground(x, QtGui.QBrush(QtGui.QColor(150, 150, 200)))

        self.updateData()

    def updateData(self):
        self.setData(0, QtCore.Qt.DisplayRole, self._node.name)
        self.setFont(0, QtGui.QFont(constants.FONT_NAME, constants.FONT_SIZE, QtGui.QFont.Bold))
        self.setData(7, QtCore.Qt.DisplayRole, self.reportStatus)


class ValidityTreeWidgetItem(TreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        assert isinstance(node, ConnectionValidityNode), "validityNode is not an instance of ConnectionValidityNode!"
        super(ValidityTreeWidgetItem, self).__init__(node=node, *args, **kwargs)
        self.setIcon(0, cui_theme.QIcon(themeName="core", iconName="connection"))

        for x in range(1, 7):
            self.setBackground(x, QtGui.QBrush(QtGui.QColor(255 ,255, 153)))

        self.updateData()

    def updateData(self):
        self.setData(1, QtCore.Qt.DisplayRole, self._node.destAttrName)
        self.setFont(1, QtGui.QFont(constants.FONT_NAME, constants.FONT_SIZE, QtGui.QFont.Bold))

        self.setData(2, QtCore.Qt.DisplayRole, self._node.destAttrValue)

        self.setData(4, QtCore.Qt.DisplayRole, self._node.name)
        self.setFont(4, QtGui.QFont(constants.FONT_NAME, constants.FONT_SIZE, QtGui.QFont.Bold))

        self.setData(5, QtCore.Qt.DisplayRole, self._node.srcAttrName)

        self.setData(6, QtCore.Qt.DisplayRole, self._node.srcAttrValue)

        self.setData(7, QtCore.Qt.DisplayRole, self.reportStatus)
        self.setFont(7, QtGui.QFont(constants.FONT_NAME, constants.FONT_SIZE, QtGui.QFont.Bold))


class DefaultTreeWidgetItem(TreeWidgetItem):
    def __init__(self, node, *args, **kwargs):
        assert isinstance(node, DefaultValueNode), "defaultNode is not an instance of DefaultValueNode!"
        super(DefaultTreeWidgetItem, self).__init__(node=node, *args, **kwargs)
        self.setIcon(0, cui_theme.QIcon(themeName="core", iconName="defaultvalue"))

        for x in range(1, 4):
            self.setBackground(x, QtGui.QBrush(QtGui.QColor(100, 200, 100)))

        self.updateData()

    def updateData(self):
        self.setData(1, QtCore.Qt.DisplayRole, self._node.name)
        self.setFont(1, QtGui.QFont(constants.FONT_NAME, constants.FONT_SIZE, QtGui.QFont.Bold))

        self.setData(2, QtCore.Qt.DisplayRole, str(self._node.defaultValue))

        self.setData(4, QtCore.Qt.DisplayRole, "")

        self.setData(5, QtCore.Qt.DisplayRole, "")

        self.setData(6, QtCore.Qt.DisplayRole, "")

        self.setData(7, QtCore.Qt.DisplayRole, self.reportStatus)
        self.setFont(7, QtGui.QFont(constants.FONT_NAME, constants.FONT_SIZE, QtGui.QFont.Bold))
