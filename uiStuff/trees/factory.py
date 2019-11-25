#  Copyright (c) 2019.  James Dunlop
import copy
from PySide2 import QtCore, QtGui
from core import nodes as c_nodes
from uiStuff.trees import treewidgetitems
from uiStuff.themes import factory as cui_theme
from const import serialization as c_serialization
QTDISPLAYROLE = QtCore.Qt.DisplayRole
SOURCENODE_COLOR = QtGui.QColor(150, 150, 200)
CONNECTIONNODE_COLOR = QtGui.QColor(255, 255, 153)
DEFAULTNODE_COLOR = QtGui.QColor(100, 200, 100)


def treeWidgetItemFromNode(node):
    """
    :param node: Instance of Node, SourceNode, etc etc
    :type node: `c_nodes.Node`
    :return: `treewidgetitems.TreeWidgetItem`
    """
    defaultdata = {0: (QTDISPLAYROLE, node.name), 7: (QTDISPLAYROLE, node.status)}

    twi = treewidgetitems.TreeWidgetItem(node=node)

    if node.nodeType == c_serialization.NT_SOURCENODE:
        rowdata = defaultdata
        colorRowRange = (1, 7)
        colorRowBrush = QtGui.QBrush(SOURCENODE_COLOR)
        iconName = "defaultvalue"

    elif node.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
        rowdata = setConnectionValidityNodeData(node, defaultdata)
        colorRowRange = (1, 7)
        colorRowBrush = QtGui.QBrush(CONNECTIONNODE_COLOR)
        iconName = "connection"

    else:
        rowdata = setDefaultValueNodeData(node, defaultdata)
        colorRowRange = (1, 4)
        colorRowBrush = QtGui.QBrush(DEFAULTNODE_COLOR)
        iconName = "defaultvalue"


    twi.updateData(rowdata)
    setRowColors(twi, colorRowRange, colorRowBrush)
    setTWIIcon(twi, iconName)

    return twi

def setRowColors(twi, colorRowRange, colorRowBrush):
    """

    :type twi: `treewidgetitems.BaseTreeWidgetItem`
    :type colorRowRange: `tuple`
    :type colorRowBrush: `QtGui.QBrush`
    :return: None
    """
    for x in range(colorRowRange[0], colorRowRange[1]):
        twi.setBackground(x, colorRowBrush)

def setConnectionValidityNodeData(node, rowdata):
    d = rowdata.copy()
    d[1] = (QTDISPLAYROLE, node.srcAttrName)
    d[2] = (QTDISPLAYROLE, node.srcAttrValue)
    d[4] = (QTDISPLAYROLE, node.name)
    d[5] = (QTDISPLAYROLE, node.destAttrName)
    d[6] = (QTDISPLAYROLE, node.destAttrValue)

    return d

def setDefaultValueNodeData(node, rowdata):
    d = rowdata.copy()
    d[1] = (QTDISPLAYROLE, node.name)
    d[2] = (QTDISPLAYROLE, str(node.defaultValue))
    d[4] = (QTDISPLAYROLE, "--")
    d[5] = (QTDISPLAYROLE, "--")
    d[6] = (QTDISPLAYROLE, "--")

    return d

def setTWIIcon(twi, iconName):
    twi.setIcon(0, cui_theme.QIcon(themeName="core", iconName=iconName))
