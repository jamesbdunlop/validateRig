#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtCore
from core import nodes as c_nodes
from uiStuff.trees import treewidgetitems
from const import serialization as c_serialization

logger = logging.getLogger(__name__)

QTDISPLAYROLE = QtCore.Qt.DisplayRole
SEPARATOR = "--"


def treeWidgetItemFromNode(node):
    """
    :param node: Instance of Node, SourceNode, etc etc
    :type node: `c_nodes.Node`
    :return: `treewidgetitems.TreeWidgetItem`
    """
    twi = treewidgetitems.TreeWidgetItem(node=node)
    rowdataDict = {0: (QTDISPLAYROLE, node.name), 7: (QTDISPLAYROLE, node.status)}

    if node.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
        rowsData = (
            (1, QTDISPLAYROLE, node.srcAttrName),
            (2, QTDISPLAYROLE, node.srcAttrValue),
            (4, QTDISPLAYROLE, node.name),
            (5, QTDISPLAYROLE, node.destAttrName),
            (6, QTDISPLAYROLE, node.destAttrValue),
        )
        rowdataDict = appendRowData(rowdataDict, rowsData)

    elif node.nodeType == c_serialization.NT_DEFAULTVALUE:
        rowsData = (
            (1, QTDISPLAYROLE, node.name),
            (2, QTDISPLAYROLE, str(node.defaultValue)),
            (4, QTDISPLAYROLE, SEPARATOR),
            (5, QTDISPLAYROLE, SEPARATOR),
            (6, QTDISPLAYROLE, SEPARATOR),
        )
        rowdataDict = appendRowData(rowdataDict, rowsData)

    twi.updateData(data=rowdataDict)

    return twi

def appendRowData(rowdataDict, rowData):
    """

    :param rowData: Tuple holding the rowData (rowNumber, QtRole, Value)
    :type rowdataDict: `dict`
    :type rowData: `tuple`
    :return: `dict`
    """
    d = rowdataDict.copy() #Shallow copy should be fine here.
    for rowNumber, role, value in rowData:
        d[rowNumber] = (role, value)

    return d
