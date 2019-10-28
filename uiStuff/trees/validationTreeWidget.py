import logging
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
        self.customContextMenuRequested.connect(self.__rightClickMenu)
        self.resizeColumnToContents(True)
        self.setAcceptDrops(True)
        self.setColumnCount(8)
        self.setHeaderLabels(constants.HEADER_LABELS)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.widgetUnderMouse = None
        self._validator = validator

    def __getNodeTypeUnderCursor(self, QPoint):
        twi = self.itemAt(QPoint)
        if twi is None:
            return -1

        return twi.node().nodeType

    def __rightClickMenu(self, QPoint):
        """
        Construct node appropriate menu + actions

        :param QPoint: `QPoint`
        :return:
        """
        menu = QtWidgets.QMenu()
        nodeType = self.__getNodeTypeUnderCursor(QPoint)
        if not nodeType:
            return

        if nodeType == c_serialization.NT_SOURCENODE:
            removeSourceNodes = menu.addAction("Remove SourceNode(s)")
            removeSourceNodes.triggered.connect(self.__removeTopLevelItems)
            removeAll = menu.addAction("Remove ALL SourceNode ValidationNodes")
            removeAll.triggered.connect(self.__removeAllChildren)

        elif nodeType == c_serialization.NT_CONNECTIONVALIDITY or nodeType == c_serialization.NT_DEFAULTVALUE:
            remove = menu.addAction("Remove ValidationNode")
            remove.triggered.connect(self.__removeTreeWidgetItems)

        else:
            clearAll = menu.addAction("Clear ALL SourceNodes")
            clearAll.triggered.connect(self.__removeAllTopLevelItems)

        menu.exec_(menu.mapToGlobal(QtGui.QCursor.pos()))

    def _processSourceNodeAttributeWidget(self, srcDataList):
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
                self.addTopLevelItem(twi)

            else:
                # Find existing treeWidgetItem, remove them from the tree and add fresh Validity Nodes
                # Assuming only 1 ever exists!
                widgetList = self.findItems(existing_srcNode.name, QtCore.Qt.MatchExactly)
                if not widgetList:
                    continue

                twi = widgetList[0]
                # Kinda annoying but QT sucks at just using childCount() for some reason! Most likely the data changes
                # out from under and it just hangs onto the last one or something odd.
                while twi.childCount():
                    for x in range(twi.childCount()):
                        twi.takeChild(x)

            # Populate the validation rows with validity nodes
            for eachValidityNode in srcNode.iterValidityNodes():
                if eachValidityNode.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                    twi.addChild(cuit_treewidgetitems.ConnectionValidityTreeWidgetItem(node=eachValidityNode))

                if eachValidityNode.nodeType == c_serialization.NT_DEFAULTVALUE:
                    twi.addChild(cuit_treewidgetitems.DefaultValueTreeWidgetItem(node=eachValidityNode))

    def validator(self):
        return self._validator

    def __removeTreeWidgetItems(self):
        """
        Normally I'd consider just altering the data and redrawing everything, but I'm expecting this stuff to bloat
        pretty quicky on large rigs so I'm looking to edit ONLY the rows I want for now and directly removing the data
        from the validator / sourceNodes as required.
        """
        for eachTreeWidgetItem in self.selectedItems():
            # Remove the data
            sourceNode = eachTreeWidgetItem.parent().node()
            sourceNode.removeValidityNode(eachTreeWidgetItem.node())
            # Now the treeWidgetItems
            eachTreeWidgetItem.parent().removeChild(eachTreeWidgetItem)

    def __removeAllChildren(self):
        for eachTreeWidgetItem in self.selectedItems():
            eachTreeWidgetItem.removeAllChildren()

    def __removeTopLevelItems(self):
        for eachTreeWidgetItem in self.selectedItems():
            sourceNode = eachTreeWidgetItem.node()
            self.validator().removeSourceNode(sourceNode)

            idx = self.indexOfTopLevelItem(eachTreeWidgetItem)
            self.takeTopLevelItem(idx)

    def __removeAllTopLevelItems(self):
        while self.topLevelItemCount():
            for x in range(self.topLevelItemCount()):
                item = self.topLevelItem(x)
                if item is None:
                    continue

                sourceNode = item.node()
                self.validator().removeSourceNode(sourceNode)
                self.takeTopLevelItem(x)

    # Drag and Drop
    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationTreeWidget, self).dragEnterEvent(QDragEnterEvent)
        return QDragEnterEvent.accept()

    def dragMoveEvent(self, QDragMoveEvent):
        super(ValidationTreeWidget, self).dragMoveEvent(QDragMoveEvent)
        return QDragMoveEvent.accept()

    def dropEvent(self, QDropEvent):
        super(ValidationTreeWidget, self).dropEvent(QDropEvent)


class MayaValidationTreeWidget(ValidationTreeWidget):
    def __init__(self, validator, parent=None):
        super(MayaValidationTreeWidget, self).__init__(validator=validator, parent=parent)

    def processMayaDrop(self, QDropEvent):
        nodeNames = QDropEvent.mimeData().text().split("\n")

        # Check to see if this exists in the validator we dropped over.
        for nodeName in nodeNames:
            existingSourceNode = None
            sourceNodeName = nodeName.split("|")[-1]
            if self.validator().sourceNodeNameExists(sourceNodeName):
                existingSourceNode = self.validator().findSourceNodeByName(sourceNodeName)

            if existingSourceNode is not None:
                self.srcNodesWidget = uid_attributeList.MayaSourceNodeAttributeListWidget.fromSourceNode(sourceNode=existingSourceNode, parent=self)
            else:
                self.srcNodesWidget = uid_attributeList.MayaSourceNodeAttributeListWidget(nodeName=nodeName, parent=self)

            if self.srcNodesWidget is None:
                continue

            self.srcNodesWidget.addSrcNodes.connect(self._processSourceNodeAttributeWidget)
            self.srcNodesWidget.move(QtGui.QCursor.pos())
            self.srcNodesWidget.resize(600, 900)
            self.srcNodesWidget.show()

    def dropEvent(self, QDropEvent):
        super(MayaValidationTreeWidget, self).dropEvent(QDropEvent)
        if not inside.insideMaya():
            return None

        self.processMayaDrop(QDropEvent)
