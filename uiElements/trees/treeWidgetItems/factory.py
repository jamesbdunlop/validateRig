#  Copyright (C) Animal Logic Pty Ltd. All rights reserved.
import logging
from PySide2 import QtCore, QtWidgets

from validateRig import insideDCC as vr_insideDCC
from validateRig.const import serialization as vrc_serialization
from validateRig.const import constants as vrconst_constants
from validateRig.core import nodes as vrc_nodes
from validateRig.uiElements.trees.treeWidgetItems import treewidgetitems as vruiettwi_treewidgetitems

logger = logging.getLogger(__name__)

QTDISPLAYROLE = QtCore.Qt.DisplayRole


def treeWidgetItemFromNode(node):
    # type: (vrc_nodes.Node) -> QtWidgets.TreeWidgetItem
    """:param node: Instance of Node, SourceNode, etc etc"""
    twi = vruiettwi_treewidgetitems.TreeWidgetItem(node=node)

    rowdataDict = {
        vrconst_constants.REPORTSTATUS_COLUMN: (QTDISPLAYROLE, node.status),
    }

    if node.nodeType == vrc_serialization.NT_SOURCENODE:
        rowdataDict = appendRowData(
            rowdataDict,
            ((vrconst_constants.SRC_NODENAME_COLUMN, QTDISPLAYROLE, node.displayName),),
        )

    elif node.nodeType == vrc_serialization.NT_CONNECTIONVALIDITY:
        data = node.connectionData
        srcData = data.get("srcData", None)
        destData = data.get("destData", None)

        srcAttrName = srcData.get("attrName", None)
        srcAttrValue = srcData.get("attrValue", None)

        destAttrValue = destData.get("attrValue", None)
        destNodeName = destData.get("nodeName", None)
        destNodeLongName = destData.get("nodeLongName", None)
        destPlugData = destData.get("plugData", None)

        _, _, destPlugName, _ = destPlugData[0] #first in the list is actually the last connected plug.

        rowsData = (
            (vrconst_constants.SRC_ATTR_COLUMN, QTDISPLAYROLE, srcAttrName),
            (vrconst_constants.SRC_ATTRVALUE_COLUMN, QTDISPLAYROLE, srcAttrValue),

            (vrconst_constants.DEST_NODENAME_COLUMN, QTDISPLAYROLE, destNodeName),
            (vrconst_constants.DEST_ATTR_COLUMN, QTDISPLAYROLE, destPlugName),
            (vrconst_constants.DEST_ATTRVALUE_COLUMN, QTDISPLAYROLE, destAttrValue),
        )
        rowdataDict = appendRowData(rowdataDict, rowsData)

    elif node.nodeType == vrc_serialization.NT_DEFAULTVALUE:
        data = node.defaultValueData
        for eachDefaultValue, value in data.iteritems():
            rowsData = (
                (vrconst_constants.SRC_ATTR_COLUMN, QTDISPLAYROLE, eachDefaultValue),
                (vrconst_constants.SRC_ATTRVALUE_COLUMN, QTDISPLAYROLE, str(value)),
                (
                    vrconst_constants.DEST_NODENAME_COLUMN,
                    QTDISPLAYROLE,
                    vrconst_constants.SEPARATOR,
                ),
                (vrconst_constants.DEST_ATTR_COLUMN, QTDISPLAYROLE, vrconst_constants.SEPARATOR),
                (
                    vrconst_constants.DEST_ATTRVALUE_COLUMN,
                    QTDISPLAYROLE,
                    vrconst_constants.SEPARATOR,
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
    # type: (vrc_nodes.Node, QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem) -> None
    setButton = QtWidgets.QPushButton("Set")

    if node.nodeType == vrc_serialization.NT_SOURCENODE:
        label = QtWidgets.QLabel(node.name)
        treewidget.setItemWidget(twi, vrconst_constants.SRC_NODENAME_COLUMN, label)

    elif node.nodeType == vrc_serialization.NT_CONNECTIONVALIDITY:
        treewidget.setItemWidget(twi, vrconst_constants.SRC_NODENAME_COLUMN, setButton)

    elif node.nodeType == vrc_serialization.NT_DEFAULTVALUE:
        treewidget.setItemWidget(twi, vrconst_constants.SRC_NODENAME_COLUMN, setButton)
