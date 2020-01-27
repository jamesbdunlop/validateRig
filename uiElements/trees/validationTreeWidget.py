#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtWidgets, QtCore, QtGui

from validateRig.api import vrigCoreApi
from validateRig.const import constants as vrconst_constants
from validateRig.const import serialization as c_serialization
from validateRig.core.validator import Validator
from validateRig.core.nodes import SourceNode
from validateRig.uiElements.trees.treeWidgetItems import factory as cuitwi_factory

logger = logging.getLogger(__name__)


class ValidationTreeWidget(QtWidgets.QTreeWidget):
    remove = QtCore.Signal(list, name="remove")
    updateNode = QtCore.Signal(object, name='updateNode')

    def __init__(self, validator, parent=None):
        # type: (Validator, QtWidgets.QWidget) -> None
        super(ValidationTreeWidget, self).__init__(parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__rightClickMenu)
        self.resizeColumnToContents(True)
        self.setAcceptDrops(True)
        self.setColumnCount(8)
        self.setHeaderLabels(vrconst_constants.HEADER_LABELS)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.widgetUnderMouse = None
        self._validator = validator
        delegate = Delegate()
        self.setItemDelegate(delegate)

    def validator(self):
        return self._validator

    def iterTopLevelTreeWidgetItems(self):
        for x in range(self.topLevelItemCount()):
            treeWidgetItem = self.topLevelItem(x)
            yield treeWidgetItem

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
            updateFromDCC = menu.addAction("Update from DCC")
            if nodeType == c_serialization.NT_DEFAULTVALUE:
                updateFromDCC.triggered.connect(self.updateDefaultValueFromDCC)
            else:
                updateFromDCC.triggered.connect(self.updateConnectionNodeSrcAttrValueFromScene)

            remove = menu.addAction("Remove ValidationNode")
            remove.triggered.connect(self.__removeSelectedTreeWidgetItems)

        else:
            clearAll = menu.addAction("Clear ALL SourceNodes")
            clearAll.triggered.connect(self.__removeAllTopLevelItems)

        menu.exec_(menu.mapToGlobal(QtGui.QCursor.pos()))

    def __removeValidator(self):
        self.remove.emit([self.validator(), self.parent()])

    def __addTopLevelTreeWidgetItemFromSourceNode(self, sourceNode):
        # type: (SourceNode) -> QtWidgets.QTreeWidgetItem
        item = cuitwi_factory.treeWidgetItemFromNode(node=sourceNode)
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
        logger.info("Removing all twi children")
        while treeWidgetItem.childCount():
            for x in range(treeWidgetItem.childCount()):
                treeWidgetItem.takeChild(x)

    def _processSourceNodeAttributeWidgets(self, sourceNodesList):
        # type: (list[SourceNode]) -> None
        for sourceNode in sourceNodesList:
            existingSourceNode = self.validator().findSourceNodeByLongName(sourceNode.longName)
            logger.info("Found existingSourceNode %s" % existingSourceNode.longName)
            if existingSourceNode is not None:
                treeWidgetItem = self.__findTreeWidgetItemByExactName(sourceNode.displayName)
                if treeWidgetItem is None:
                    logger.info("Didn't find treeWidgetItem for %s" % sourceNode.displayName)
                    treeWidgetItem = self.__addTopLevelTreeWidgetItemFromSourceNode(sourceNode)
                    ValidationTreeWidget.addValidityNodesToTreeWidgetItem(sourceNode, treeWidgetItem)
                    continue

                self.__removeAllTreeWidgetItemChildren(treeWidgetItem)
                ValidationTreeWidget.addValidityNodesToTreeWidgetItem(sourceNode, treeWidgetItem)
                continue

            # New
            self.validator().addSourceNode(sourceNode, True)
            treeWidgetItem = self.__addTopLevelTreeWidgetItemFromSourceNode(sourceNode)
            ValidationTreeWidget.addValidityNodesToTreeWidgetItem(sourceNode, treeWidgetItem)

    def __removeSelectedTreeWidgetItems(self):
        for eachTreeWidgetItem in self.selectedItems():
            node = eachTreeWidgetItem.parent().node()
            node.removeChild(eachTreeWidgetItem.node())

            sourceNodeTreeWidgetItem = eachTreeWidgetItem.parent()
            sourceNodeTreeWidgetItem.removeChild(eachTreeWidgetItem)

            existingSourceNode = self.validator().findSourceNodeByLongName(eachTreeWidgetItem.node().longName)
            self.validator().removeSourceNode(existingSourceNode)

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

    def updateDefaultValueFromDCC(self):
        for eachTreeWidgetItem in self.selectedItems():
            defaultValueNode = eachTreeWidgetItem.node()
            self.updateNode.emit(defaultValueNode)
            eachTreeWidgetItem.updateDefaultValue()

    def updateConnectionNodeSrcAttrValueFromScene(self):
        for eachTreeWidgetItem in self.selectedItems():
            connectionNode = eachTreeWidgetItem.node()
            self.updateNode.emit(connectionNode)
            eachTreeWidgetItem.updateConnectionValue()

            for eachChild in eachTreeWidgetItem.children:
                connectionNode = eachChild.node()
                self.updateNode.emit(connectionNode)
                eachChild.updateConnectionValue()

    # Drag and Drop
    def dragEnterEvent(self, QDragEnterEvent):
        super(ValidationTreeWidget, self).dragEnterEvent(QDragEnterEvent)
        return QDragEnterEvent.accept()

    def dragMoveEvent(self, QDragMoveEvent):
        super(ValidationTreeWidget, self).dragMoveEvent(QDragMoveEvent)
        return QDragMoveEvent.accept()

    def dropEvent(self, QDropEvent):
        super(ValidationTreeWidget, self).dropEvent(QDropEvent)
        nodeNames = QDropEvent.mimeData().text().split("\n")
        self.attrWidget = vrigCoreApi.processValidationTreeWidgetDropEvent(nodeNames, self.validator, parent=None)
        self.attrWidget.sourceNodesAccepted.connect(self._processSourceNodeAttributeWidgets)
        self.attrWidget.move(QtGui.QCursor.pos())
        self.attrWidget.show()

    # Clicks
    def mouseDoubleClickEvent(self, event=QtGui.QMouseEvent):
        nodeNames = list()
        for eachItem in self.selectedItems():
            node = eachItem.node()
            nodeType = node.nodeType
            if nodeType == c_serialization.NT_SOURCENODE:
                itemName = eachItem.data(0, QtCore.Qt.DisplayRole)

            elif nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                itemName = eachItem.data(4, QtCore.Qt.DisplayRole)

            elif nodeType == c_serialization.NT_DEFAULTVALUE:
                sourceNodeTWI = eachItem.parent()
                itemName = sourceNodeTWI.data(0, QtCore.Qt.DisplayRole)

            else:
                itemName = ""

            nodeNames.append(itemName)

        vrigCoreApi.selectNodesInDCC(nodeNames, event)

    @staticmethod
    def addValidityNodesToTreeWidgetItem(sourceNode, sourceNodeTreeWItm):
        # type: (Node, QtWidgets.QTreeWidgetItem) -> None
        connectionAttrSrcNames = list()
        parentNode = None

        for eachValidityNode in sourceNode.iterChildren():
            treewidgetItem = cuitwi_factory.treeWidgetItemFromNode(node=eachValidityNode)

            if eachValidityNode.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                data = eachValidityNode.connectionData
                srcData = data.get("srcData", None)
                srcAttrName = srcData.get("attrName", None)
                if srcAttrName not in connectionAttrSrcNames:
                    connectionAttrSrcNames.append(srcAttrName)
                    sourceNodeTreeWItm.addChild(treewidgetItem)

                    # First found becomes the parentNode!
                    parentNode = treewidgetItem
                else:
                    # parent this to the parentNode
                    parentNode.addChild(treewidgetItem)
            else:
                sourceNodeTreeWItm.addChild(treewidgetItem)
            # Crashes maya
            # cuitwi_factory.setSourceNodeItemWidgetsFromNode(
            #     node=eachValidityNode, treewidget=treeWidget, twi=treewidgetItem
            # )


class Delegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, qmodelidx):
        super(Delegate, self).paint(painter, option, qmodelidx)

        painter.save()
        if qmodelidx.isValid():
            model = qmodelidx.model()
            data = model.data(qmodelidx, QtCore.Qt.DisplayRole)
            if data is None:
                return

        painter.restore()
