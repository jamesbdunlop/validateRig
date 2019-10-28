import logging
from functools import partial
from PySide2 import QtWidgets, QtCore, QtGui
from const import constants
from const import serialization as c_serialization
from core import inside
from uiStuff.trees import treewidgetitems as cuit_treewidgetitems
from uiStuff.dialogs import attributeList as uid_attributeList

logger = logging.getLogger(__name__)

if inside.insideMaya():
    import maya.cmds as cmds


class ValidationTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, validator, parent=None):
        """

        :param contextMenu: `QMenu`
        :param validator: `Validator`
        :param parent: `QtParent`
        """
        super(ValidationTreeWidget, self).__init__(parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._TreeViewRCMenu)
        self.resizeColumnToContents(True)
        self.setAcceptDrops(True)
        self.setColumnCount(8)
        self.setHeaderLabels(constants.HEADER_LABELS)
        self.widgetUnderMouse = None
        self._validator = validator

    def __getNodeTypeUnderCursor(self, QPoint):
        twi = self.itemAt(QPoint)
        if twi is None:
            return -1

        return twi.node().nodeType

    def _TreeViewRCMenu(self, QPoint):
        menu = QtWidgets.QMenu()
        nodeType = self.__getNodeTypeUnderCursor(QPoint)
        if not nodeType:
            return

        if nodeType == c_serialization.NT_SOURCENODE:
            removeAll = menu.addAction("Remove All Validators")
            removeAll.triggered.connect(partial(self.__removeAllChildren, QPoint))

        elif nodeType == c_serialization.NT_CONNECTIONVALIDITY or nodeType == c_serialization.NT_DEFAULTVALUE:
            remove = menu.addAction("Remove validation node")
            remove.triggered.connect(partial(self.__removeTreeWidgetItem, QPoint))

        else:
            menu.addAction("AddSource")
            clearAll = menu.addAction("clear All")
            clearAll.triggered.connect(self.__removeAllTopLevelItems)

        menu.exec_(menu.mapToGlobal(QtGui.QCursor.pos()))

    def addSourceNodeDataFromSourceNodeAttributeWidget(self, srcDataList):
        """

        :param srcDataList: `list`
        :return: `None`
        """
        for srcNode in srcDataList:
            existing_srcNode = self.validator().findSourceNodeByName(srcNode.name)

            if existing_srcNode is None:
                self.validator().addSourceNode(srcNode, True)

                # Create and add the treeWidgetItem to the treeWidget from the node
                twi = cuit_treewidgetitems.SourceTreeWidgetItem(node=srcNode)
                self._validators[-1][1].addTopLevelItem(twi)

            else:
                # Find existing treeWidgetItem, remove them from the tree and add fresh Validity Nodes
                treeWidget = self._validators[-1][1]

                # Assuming only 1 ever exists!
                widgetList = treeWidget.findItems(existing_srcNode.name, QtCore.Qt.MatchExactly)
                if not widgetList:
                    continue

                twi = widgetList[0]
                for x in range(twi.childCount()):
                    twi.takeChild(x)

            # Populate the validation rows with validity nodes
            for eachVN in srcNode.iterValidityNodes():
                if eachVN.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                    twi.addChild(cuit_treewidgetitems.ValidityTreeWidgetItem(node=eachVN))

                if eachVN.nodeType == c_serialization.NT_DEFAULTVALUE:
                    twi.addChild(cuit_treewidgetitems.DefaultTreeWidgetItem(node=eachVN))

    def validator(self):
        return self._validator

    def __removeTreeWidgetItem(self, QPoint):
        self.itemAt(QPoint).parent().removeChild(self.itemAt(QPoint))

    def __removeAllChildren(self, QPoint):
        self.itemAt(QPoint).removeAllChildren()

    def __removeAllTopLevelItems(self):
        while self.topLevelItemCount():
            for x in range(self.topLevelItemCount()):
                self.takeTopLevelItem(x)

    # Drag and Drop
    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationTreeWidget, self).dragEnterEvent(QDragEnterEvent)
        return QDragEnterEvent.accept()

    def dragMoveEvent(self, QDragMoveEvent):
        itemAt = self.itemAt(QDragMoveEvent.pos())
        if itemAt.parent() is None:
            self.widgetUnderMouse = itemAt
        else:
            self.widgetUnderMouse = itemAt.parent()

    def dropEvent(self, QDropEvent):
        super(ValidationTreeWidget, self).dropEvent(QDropEvent)
        if inside.insideMaya():
            self.processMayaDrop(QDropEvent)

    def processMayaDrop(self, QDropEvent):
        if not inside.insideMaya() or self.widgetUnderMouse is None:
            return

        nodeNames = QDropEvent.mimeData().text().split("\n")

        # Check to see if this exists in the validator we dropped over.
        for nodeName in nodeNames:
            existingSrcNode = self.validator().sourceNodeExists(nodeName.split("|")[-1])
            if existingSrcNode:
                self.srcNodesWidget = uid_attributeList.SourceNodeAttributeListWidget().fromSourceNode(sourceNode=existingSrcNode)
            else:
                self.srcNodesWidget = uid_attributeList.SourceNodeAttributeListWidget(nodeName=nodeName, parent=self)

            if self.srcNodesWidget is None:
                continue

            self.srcNodesWidget.addSrcNodes.connect(self.addSourceNodeDataFromSourceNodeAttributeWidget)
            self.srcNodesWidget.move(QtGui.QCursor.pos())
            self.srcNodesWidget.resize(600, 900)
            self.srcNodesWidget.show()
