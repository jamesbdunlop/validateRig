#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtCore, QtWidgets
from core import nodes as c_nodes
from uiElements.trees import treewidgetitems
from const import serialization as c_serialization
from const import constants as vrc_constants
import inside as c_inside
logger = logging.getLogger(__name__)

QTDISPLAYROLE = QtCore.Qt.DisplayRole


def treeWidgetItemFromNode(node):
    # type: (c_nodes.Node) -> treewidgetitems.TreeWidgetItem
    """:param node: Instance of Node, SourceNode, etc etc"""
    twi = treewidgetitems.TreeWidgetItem(node=node)

    rowdataDict = {
        vrc_constants.REPORTSTATUS_COLUMN: (QTDISPLAYROLE, node.status),
    }

    if node.nodeType == c_serialization.NT_SOURCENODE:
        rowdataDict = appendRowData(
            rowdataDict,
            ((vrc_constants.SRC_NODENAME_COLUMN, QTDISPLAYROLE, node.displayName),),
        )

    elif node.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
        data = node.connectionData
        if c_inside.insideMaya():
            srcData = data.get("srcData", None)
            destData = data.get("destData", None)

            srcAttrName = srcData.get("attrName", None)
            srcAttrValue = srcData.get("attrValue", None)

            destNodeName = destData.get("nodeName", None)
            destAttrValue = destData.get("attrValue", None)
            destPlugData = destData.get("plugData", None)

            _, _, destPlugName, _ = destPlugData[0]

            rowsData = (
                (vrc_constants.SRC_ATTR_COLUMN, QTDISPLAYROLE, srcAttrName),
                (vrc_constants.SRC_ATTRVALUE_COLUMN, QTDISPLAYROLE, srcAttrValue),

                (vrc_constants.DEST_NODENAME_COLUMN, QTDISPLAYROLE, destNodeName),
                (vrc_constants.DEST_ATTR_COLUMN, QTDISPLAYROLE, destPlugName),
                (vrc_constants.DEST_ATTRVALUE_COLUMN, QTDISPLAYROLE, destAttrValue),
            )

        rowdataDict = appendRowData(rowdataDict, rowsData)

    elif node.nodeType == c_serialization.NT_DEFAULTVALUE:
        data = node.defaultValueData
        for eachDefaultValue, value in data.iteritems():
            rowsData = (
                (vrc_constants.SRC_ATTR_COLUMN, QTDISPLAYROLE, eachDefaultValue),
                (vrc_constants.SRC_ATTRVALUE_COLUMN, QTDISPLAYROLE, str(value)),
                (
                    vrc_constants.DEST_NODENAME_COLUMN,
                    QTDISPLAYROLE,
                    vrc_constants.SEPARATOR,
                ),
                (vrc_constants.DEST_ATTR_COLUMN, QTDISPLAYROLE, vrc_constants.SEPARATOR),
                (
                    vrc_constants.DEST_ATTRVALUE_COLUMN,
                    QTDISPLAYROLE,
                    vrc_constants.SEPARATOR,
                ),
            )
            rowdataDict = appendRowData(rowdataDict, rowsData)

    for colID, data in rowdataDict.items():
        qtRole = data[0]
        value = data[1]
        twi.updateColumnData(columnId=colID, qtRole=qtRole, value=value)

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
        treewidget.setItemWidget(twi, vrc_constants.SRC_NODENAME_COLUMN, label)

    elif node.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
        treewidget.setItemWidget(twi, vrc_constants.SRC_NODENAME_COLUMN, setButton)

    elif node.nodeType == c_serialization.NT_DEFAULTVALUE:
        treewidget.setItemWidget(twi, vrc_constants.SRC_NODENAME_COLUMN, setButton)
