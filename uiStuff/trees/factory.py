#  Copyright (c) 2019.  James Dunlop
from PySide2 import QtCore, QtGui
from core import nodes as c_nodes
from uiStuff.trees import treewidgetitems
from uiStuff.themes import factory as cui_theme

def treeWidgetItemFromNode(node):
    """
    :param node: Instance of Node, SourceNode, etc etc
    :type node: `c_nodes.Node`
    :return:
    """
    data = {0: (QtCore.Qt.DisplayRole, node.name),
            7: (QtCore.Qt.DisplayRole, node.status)
            }
    twi = treewidgetitems.BaseTreeWidgetItem(node=node)

    if isinstance(node, c_nodes.SourceNode):
        setRowColors(twi, 1, 7, QtGui.QBrush(QtGui.QColor(150, 150, 200)))

    elif isinstance(node, c_nodes.ConnectionValidityNode):
        data[1] = (QtCore.Qt.DisplayRole, node.srcAttrName)
        data[2] = (QtCore.Qt.DisplayRole, node.srcAttrValue)
        data[4] = (QtCore.Qt.DisplayRole, node.name)
        data[5] = (QtCore.Qt.DisplayRole, node.destAttrName)
        data[6] = (QtCore.Qt.DisplayRole, node.destAttrValue)

        setRowColors(twi, 1, 7, QtGui.QBrush(QtGui.QColor(255, 255, 153)))
        twi.setIcon(0, cui_theme.QIcon(themeName="core", iconName="connection"))

    elif isinstance(node, c_nodes.DefaultValueNode):
        data[1] = (QtCore.Qt.DisplayRole, node.name)
        data[2] = (QtCore.Qt.DisplayRole, str(node.defaultValue))
        data[4] = (QtCore.Qt.DisplayRole, "--")
        data[5] = (QtCore.Qt.DisplayRole, "--")
        data[6] = (QtCore.Qt.DisplayRole, "--")

        setRowColors(twi, 1, 4, QtGui.QBrush(QtGui.QColor(100, 200, 100)))
        twi.setIcon(0, cui_theme.QIcon(themeName="core", iconName="defaultvalue"))

    twi.updateData(data)
    return twi

def setRowColors(twi, start, end, qbrush):
    """

    :type twi: `treewidgetitems.BaseTreeWidgetItem`
    :type start: `int`
    :type end: `int`
    :type qbrush: `QtGui.QBrush`
    :return: None
    """
    for x in range(start, end):
        twi.setBackground(x, qbrush)
