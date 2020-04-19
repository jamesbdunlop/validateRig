#  Copyright (C) Animal Logic Pty Ltd. All rights reserved.
import logging
from PySide2 import QtCore
from validateRig.uiElements.dialogs import validityNodeWidgets as vruied_validityNodeWidgets
from validateRig.const import constants as vrconst_constants
from validateRig.core.nodes import DefaultValueNode, ConnectionValidityNode, SourceNode
from validateRig.core.maya import plugs as vrcm_plugs
from validateRig.core.maya import utils as vrcm_utils
import maya.cmds as cmds

logger = logging.getLogger(__name__)


class MayaValidityNodesSelector(vruied_validityNodeWidgets.BaseSourceNodeValidityNodesSelector):
    def __init__(self, longNodeName=None, sourceNode=None, parent=None):
        # type: (str, SourceNode, QtWidgets.QWidget) -> None
        super(MayaValidityNodesSelector, self).__init__(longNodeName, sourceNode, parent)
        self._connectionData = dict()

        # Populate listWidgets
        self._populateDefaultValuesWidget()
        self._populateConnectionsWidget()

    def _populateDefaultValuesWidget(self):
        """Populates the listWidget from the longNodeName. This should be a unique name in maya or it will fail."""
        if not cmds.objExists(self._longNodeName):
            logger.warning("%s does not exist!" % self._longNodeName)
            return

        attrs = [attr for attr in cmds.listAttr(self._longNodeName) if attr not in vrconst_constants.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES]
        for eachAttribute in attrs:
            self.defaultValuesListWidget.addItem(eachAttribute)

        self.selectExistingDefaultValueNodes()

    def selectExistingDefaultValueNodes(self):
        # Select existing
        if self.sourceNode() is None:
            return

        nodeDisplayNames = [
                            node.displayName
                            for node in self.sourceNode().iterChildren()
                            if isinstance(node, DefaultValueNode)
                            ]
        for displayName in nodeDisplayNames:
            items = self.defaultValuesListWidget.findItems(
                displayName, QtCore.Qt.MatchExactly
                )
            for eachItem in items:
                if not self.defaultValuesListWidget.isItemSelected(eachItem):
                    self.defaultValuesListWidget.setItemSelected(eachItem, True)

    def _populateConnectionsWidget(self):
        """Populates the listWidget from the nodeName. This should be a unique name in maya or it will fail."""
        for destNodeName, destLongName, connectionData in vrcm_utils.createConnectionData(self._longNodeName):
            srcData = connectionData["srcData"]
            srcPlugData = srcData["plugData"]
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(self._longNodeName, srcPlugData)

            destData = connectionData["destData"]
            destNodeName = destData["nodeLongName"]
            destPlugData = destData["plugData"]
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)

            displayName = "{}{}{}".format(srcMPlug.name(), self.SEP, destMPlug.name())
            self.connsListWidget.addItem(displayName)
            self._connectionData[displayName] = [destNodeName, destLongName, connectionData]

        self.selectExistingConnections()

    def selectExistingConnections(self):
        if self.sourceNode() is None:
            return

        validationNodes = list(self.sourceNode().iterChildren())
        connectionNodes = [n for n in validationNodes if isinstance(n, ConnectionValidityNode)]
        for connectionNode in connectionNodes:
            # Not a big fan of redoing the whole mplug displayName here but leaving it for no
            # Todo clean this up
            connectionData = connectionNode.connectionData
            srcData = connectionData["srcData"]
            srcPlugData = srcData["plugData"]
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(self._longNodeName, srcPlugData)

            destData = connectionData["destData"]
            destNodeName = destData["nodeLongName"]
            destPlugData = destData["plugData"]
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)
            displayName = "{}{}{}".format(srcMPlug.name(), self.SEP, destMPlug.name())

            items = self.connsListWidget.findItems(displayName, QtCore.Qt.MatchExactly)
            for eachItem in items:
                if not self.connsListWidget.isItemSelected(eachItem):
                    self.connsListWidget.setItemSelected(eachItem, True)

    def __getValidityNodesFromDefaultValuesListWidget(self, longNodeName, defaultValuesListWidget):
        # type: (str, QtWidgets.QListWidget) -> list[DefaultValueNode]
        """
        Args:
            longNodeName: name of the node to query in maya (this is the destinationNode.longName not the
            sourceNode.longName)
        """
        nodes = list()
        for eachAttr in defaultValuesListWidget.selectedItems():
            attrName = eachAttr.text()
            value = cmds.getAttr("{}.{}".format(longNodeName, attrName))
            dvNode = DefaultValueNode(name=attrName, longName=longNodeName)
            dvNode.defaultValueData = {attrName: value}

            if self.sourceNode() is None:
                nodes.append(dvNode)
                continue

            found = False
            for validityNode in self.sourceNode().iterChildren():
                if validityNode.name == attrName:
                    found = True
            if found:
                continue

            nodes.append(dvNode)

        return nodes

    def __getValidityNodesFromConnectionsListWidget(self, connectionsListWidget):
        # type: (QtWidgets.QListWidget) -> list[ConnectionValidityNode]
        nodes = list()
        if self.sourceNode() is not None:
            connectionNodes = [n for n in self.sourceNode().iterChildren() if isinstance(n, ConnectionValidityNode)]

        for eachConnPair in connectionsListWidget.selectedItems():
            destNodeName, destLongName, connectionData = self._connectionData[eachConnPair.text()]
            destData = connectionData["destData"]
            destPlugData = destData["plugData"]
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destLongName, destPlugData)

            skip = False
            if self.sourceNode() is not None:
                # Skip existing and only pass along new connectionNodes.
                for connectionNode in connectionNodes:
                    cnConData = connectionNode.connectionData
                    cnDestData = cnConData["destData"]
                    cnDestNodeName = cnDestData["nodeLongName"]
                    cdDestPlugData = cnDestData["plugData"]
                    cnDestMPlug = vrcm_plugs.fetchMPlugFromConnectionData(cnDestNodeName, cdDestPlugData)
                    if cnDestMPlug.name() == destMPlug.name():
                        skip = True

            if skip:
                continue

            connectionNode = ConnectionValidityNode(name=destNodeName, longName=destLongName)
            connectionNode.connectionData = connectionData
            nodes.append(connectionNode)

        return nodes

    def toSourceNode(self, listWidget=None):
        # type: (BaseSourceNodeValidityNodesSelector) -> SourceNode

        sourceWidget = self
        if listWidget is not None:
            sourceWidget = listWidget

        longNodeName, defaultValuesListWidget, connsListWidget = sourceWidget._nodeData
        if listWidget is not None:
            longNodeName, _, _ = self._nodeData

        # Collect validityNode children for the SourceNode into a list
        validityNodes = list()
        validityNodes += sourceWidget.__getValidityNodesFromDefaultValuesListWidget(
            longNodeName, defaultValuesListWidget
            )
        validityNodes += sourceWidget.__getValidityNodesFromConnectionsListWidget(
            connsListWidget
            )

        if self.sourceNode() is None:
            node =  SourceNode(
                name=longNodeName.split("|")[-1].split(":")[-1],
                longName=longNodeName,
                validityNodes=validityNodes,
                )
            node.displayName = longNodeName.split("|")[-1]
            return node

        else:
            self.sourceNode().addChildren(validityNodes)
            return self.sourceNode()
