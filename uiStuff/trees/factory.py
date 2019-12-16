#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtCore, QtWidgets
from core import nodes as c_nodes
from uiStuff.trees import treewidgetitems
from vrConst import serialization as c_serialization
from vrConst import constants as cc_constants

logger = logging.getLogger(__name__)

QTDISPLAYROLE = QtCore.Qt.DisplayRole


def treeWidgetItemFromNode(node):
    # type: (c_nodes.Node) -> treewidgetitems.TreeWidgetItem
    """:param node: Instance of Node, SourceNode, etc etc"""
    twi = treewidgetitems.TreeWidgetItem(node=node)
    rowdataDict = {
        cc_constants.REPORTSTATUS_COLUMN: (QTDISPLAYROLE, node.status),
    }

    if node.nodeType == c_serialization.NT_SOURCENODE:
        rowdataDict = appendRowData(
            rowdataDict, ( (cc_constants.SRC_NODENAME_COLUMN, QTDISPLAYROLE, node.longName.split("|")[-1]), )
        )

    elif node.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
        rowsData = (
            (cc_constants.SRC_ATTR_COLUMN, QTDISPLAYROLE, node.srcAttrName),
            (cc_constants.SRC_ATTRVALUE_COLUMN, QTDISPLAYROLE, node.srcAttrValue),
            (cc_constants.DEST_NODENAME_COLUMN, QTDISPLAYROLE, node.name),
            (cc_constants.DEST_ATTR_COLUMN, QTDISPLAYROLE, node.destAttrName),
            (cc_constants.DEST_ATTRVALUE_COLUMN, QTDISPLAYROLE, node.destAttrValue),
        )
        rowdataDict = appendRowData(rowdataDict, rowsData)

    elif node.nodeType == c_serialization.NT_DEFAULTVALUE:
        rowsData = (
            (cc_constants.SRC_ATTR_COLUMN, QTDISPLAYROLE, node.name),
            (cc_constants.SRC_ATTRVALUE_COLUMN, QTDISPLAYROLE, str(node.defaultValue)),
            (cc_constants.DEST_NODENAME_COLUMN, QTDISPLAYROLE, cc_constants.SEPARATOR),
            (cc_constants.DEST_ATTR_COLUMN, QTDISPLAYROLE, cc_constants.SEPARATOR),
            (cc_constants.DEST_ATTRVALUE_COLUMN, QTDISPLAYROLE, cc_constants.SEPARATOR),
        )
        rowdataDict = appendRowData(rowdataDict, rowsData)

    twi.updateData(data=rowdataDict)

    return twi


def appendRowData(rowdataDict, rowData):
    # type: (dict, tuple) -> dict
    """:param rowData: Tuple holding the rowData (rowNumber, QtRole, Value)"""

    d = rowdataDict.copy()  # Shallow copy should be fine here.
    for rowNumber, role, value in rowData:
        d[rowNumber] = (role, value)

    return d


def setSourceNodeItemWidgetsFromNode(node, treewidget, twi):
    # type: (c_nodes.Node, QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem) -> None
    setButton = QtWidgets.QPushButton("Set")

    if node.nodeType == c_serialization.NT_SOURCENODE:
        label = QtWidgets.QLabel(node.name)
        treewidget.setItemWidget(
            twi, cc_constants.SRC_NODENAME_COLUMN, label
        )

    elif node.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
        treewidget.setItemWidget(
            twi, cc_constants.SRC_NODENAME_COLUMN, setButton
            )

    elif node.nodeType == c_serialization.NT_DEFAULTVALUE:
        treewidget.setItemWidget(
            twi, cc_constants.SRC_NODENAME_COLUMN, setButton
        )
