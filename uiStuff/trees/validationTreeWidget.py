import logging
from PySide2 import QtWidgets, QtCore, QtGui
from core import inside
from core.validator import Validator
from core.nodes import Node, SourceNode
from vrConst import constants as cc_constants
from vrConst import serialization as c_serialization
from uiStuff.trees import factory as cuit_factory
from uiStuff.dialogs import attributeList as uid_attributeList

logger = logging.getLogger(__name__)


class ValidationTreeWidget(QtWidgets.QTreeWidget):
    remove = QtCore.Signal(list, name="remove")

    def __init__(self, validator, parent=None):
        # type: (Validator, QtWidgets.QWidget) -> None
        super(ValidationTreeWidget, self).__init__(parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__rightClickMenu)
        self.resizeColumnToContents(True)
        self.setAcceptDrops(True)
        self.setColumnCount(8)
        self.setHeaderLabels(cc_constants.HEADER_LABELS)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.widgetUnderMouse = None
        self._validator = validator

    def validator(self):
        return self._validator

    def __getNodeTypeUnderCursor(self, QPoint):
        item = self.itemAt(QPoint)
        if item is None:
            return -1

        return item.node().nodeType

    def __rightClickMenu(self, QPoint):
        menu = QtWidgets.QMenu()
        removeValidator = menu.addAction("Remove Entire Validator")
        removeValidator.triggered.connect(self.__removeValidator)
        nodeType = self.__getNodeTypeUnderCursor(QPoint)
        if not nodeType:
            return

        if nodeType == c_serialization.NT_SOURCENODE:
            removeSourceNodes = menu.addAction("Remove SourceNode(s)")
            removeSourceNodes.triggered.connect(self.__removeTopLevelItems)
            removeAll = menu.addAction("Remove ALL SourceNode ValidationNodes")
            removeAll.triggered.connect(self.__removeAllChildrenFromSelectedItems)

        elif (
            nodeType == c_serialization.NT_CONNECTIONVALIDITY
            or nodeType == c_serialization.NT_DEFAULTVALUE
        ):
            remove = menu.addAction("Remove ValidationNode")
            remove.triggered.connect(self.__removeTreeWidgetItems)

        else:
            clearAll = menu.addAction("Clear ALL SourceNodes")
            clearAll.triggered.connect(self.__removeAllTopLevelItems)

        menu.exec_(menu.mapToGlobal(QtGui.QCursor.pos()))

    def __removeValidator(self):
        self.remove.emit([self.validator(), self.parent()])

    def __addTopLevelTreeWidgetItemFromSourceNode(self, sourceNode):
        # type: (SourceNode) -> QtWidgets.QTreeWidgetItem
        item = cuit_factory.treeWidgetItemFromNode(node=sourceNode)
        self.addTopLevelItem(item)

        return item

    def __findTreeWidgetItemByExactName(self, name):
        # type: (str) -> QtWidgets.QTreeWidgetItem
        """
        Args:
            name: SourceNode.name
        """
        itemList = self.findItems(name, QtCore.Qt.MatchExactly)
        if itemList:
            return itemList[0]

    def __removeAllTreeWidgetItemChildren(self, treeWidgetItem):
        # type: (QtWidgets.QTreeWidgetItem) -> None
        # Kinda annoying but QT sucks at just using childCount() for some reason! Most likely the data changes
        # out from under and it just hangs onto the last one or something odd.
        while treeWidgetItem.childCount():
            for x in range(treeWidgetItem.childCount()):
                treeWidgetItem.takeChild(x)

    def _processSourceNodeAttributeWidgets(self, sourceNodesList):
        # type: (list[SourceNode]) -> None
        for sourceNode in sourceNodesList:
            existingSourceNode = self.validator().findSourceNodeByLongName(
                sourceNode.longName
            )
            if existingSourceNode is not None:
                treeWidgetItem = self.__findTreeWidgetItemByExactName(sourceNode.name)
                if treeWidgetItem is None:
                    continue

                self.__removeAllTreeWidgetItemChildren(treeWidgetItem)
                addValidatityNodesToTreeWidgetItem(sourceNode, treeWidgetItem)
                continue

            # New
            self.validator().addSourceNode(sourceNode, True)
            treeWidgetItem = self.__addTopLevelTreeWidgetItemFromSourceNode(sourceNode)
            addValidatityNodesToTreeWidgetItem(sourceNode, treeWidgetItem)

    def __removeTreeWidgetItems(self):
        for eachTreeWidgetItem in self.selectedItems():
            node = eachTreeWidgetItem.parent().node()
            node.removeChild(eachTreeWidgetItem.node())

            sourceNodeTreeWidgetItem = eachTreeWidgetItem.parent()
            sourceNodeTreeWidgetItem.removeChild(eachTreeWidgetItem)

    def __removeAllChildrenFromSelectedItems(self):
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
        super(MayaValidationTreeWidget, self).__init__(
            validator=validator, parent=parent
        )

    def processMayaDrop(self, QDropEvent):
        nodeNames = QDropEvent.mimeData().text().split("\n")

        self.mainAttrWidget = uid_attributeList.MultiSourceNodeListWidgets(
            "SourceNodes", None
        )

        # Check to see if this exists in the validator we dropped over.
        for nodeName in nodeNames:
            nodeName = nodeName.split("|")[-1]
            if not self.validator().sourceNodeNameExists(nodeName):
                logger.info(
                    "SourceNode: {} does not exist creating new sourceNode.".format(
                        nodeName
                    )
                )
                self.srcNodesWidget = uid_attributeList.MayaValidityNodesSelector(
                    nodeName=nodeName, parent=self
                )

            else:
                logger.info("SourceNode: {} exists!".format(nodeName.split("|")[-1]))
                existingSourceNode = self.validator().findSourceNodeByLongName(nodeName)
                self.srcNodesWidget = uid_attributeList.MayaValidityNodesSelector.fromSourceNode(
                    sourceNode=existingSourceNode, parent=self
                )

            if self.srcNodesWidget is None:
                continue

            self.mainAttrWidget.addListWidget(self.srcNodesWidget)

        self.mainAttrWidget.sourceNodesAccepted.connect(
            self._processSourceNodeAttributeWidgets
        )
        self.mainAttrWidget.move(QtGui.QCursor.pos())
        self.mainAttrWidget.show()

    def dropEvent(self, QDropEvent):
        super(MayaValidationTreeWidget, self).dropEvent(QDropEvent)
        if not inside.insideMaya():
            return None

        self.processMayaDrop(QDropEvent)

    def mouseDoubleClickEvent(self, event=QtGui.QMouseEvent):
        if not inside.insideMaya():
            return

        from maya import cmds

        for eachItem in self.selectedItems():
            itemName = eachItem.data(0, QtCore.Qt.DisplayRole)
            cmds.select(itemName)
        # ValidationTreeWidget.mouseDoubleClickEvent(event)


def getValidationTreeWidget(validator, parent):
    # type: (Validator, QtWidgets.QWidget) -> QtWidgets.QTreeWidget
    """
    Args:
        validator: The validator to be used by the treeWidget
        parent: QTWidget for the treeWidget
    """

    if inside.insideMaya():
        treeWidget = MayaValidationTreeWidget(validator, parent)

    else:
        treeWidget = ValidationTreeWidget(validator, parent)

    for sourceNode in validator.iterSourceNodes():
        sourceNodeTreeWItm = cuit_factory.treeWidgetItemFromNode(node=sourceNode)
        treeWidget.addTopLevelItem(sourceNodeTreeWItm)
        addValidatityNodesToTreeWidgetItem(sourceNode, sourceNodeTreeWItm)
        # Crashes maya
        # cuit_factory.setSourceNodeItemWidgetsFromNode(
        #     node=sourceNode, treewidget=treeWidget, twi=sourceNodeTreeWItm
        # )

    treeWidget.resizeColumnToContents(0)

    return treeWidget


def addValidatityNodesToTreeWidgetItem(sourceNode, sourceNodeTreeWItm):
    # type: (Node, QtWidgets.QTreeWidgetItem) -> None
    connectionAttrSrcNames = list()
    parentNode = None
    for eachValidityNode in sourceNode.iterChildren():
        treewidgetItem = cuit_factory.treeWidgetItemFromNode(node=eachValidityNode)

        if eachValidityNode.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
            if eachValidityNode.srcAttrName not in connectionAttrSrcNames:
                connectionAttrSrcNames.append(eachValidityNode.srcAttrName)
                sourceNodeTreeWItm.addChild(treewidgetItem)
                # First found becomes the parentNode
                parentNode = treewidgetItem
            else:
                # parent this to the parentNode
                parentNode.addChild(treewidgetItem)
        else:
            sourceNodeTreeWItm.addChild(treewidgetItem)

        # Crashes maya
        # cuit_factory.setSourceNodeItemWidgetsFromNode(
        #     node=eachValidityNode, treewidget=treeWidget, twi=treewidgetItem
        # )
