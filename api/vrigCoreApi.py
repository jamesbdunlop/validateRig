#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtWidgets, QtCore
from functools import partial

from validateRig import insideDCC as vr_insideDCC
from validateRig.const import serialization as c_serialization
from validateRig.core import validator as c_validator
from validateRig.core import nodes as c_nodes
from validateRig.core import parser as c_parser
from validateRig.core import factory as c_factory
from validateRig.core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode
from validateRig.uiElements.dialogs import validityNodeWidgets as uied_validityNodeWidgets

logger = logging.getLogger(__name__)

def createValidator(name, data=None):
    # type: (str, dict) -> c_validator.Validator

    validator = c_factory.createValidator(name=name, data=data)
    return validator


def createSourceNode(name, longName, validityNodes=None):
    # type: (str, str, list[DefaultValueNode, ConnectionValidityNode]) -> None
    """
    :param validityNodes: `list` of either DefaultValueNodes or ConnectionValidityNodes
    """
    node = SourceNode(name=name, longName=longName, validityNodes=validityNodes)
    return node


def createDefaultValueNode(name, longName):
    # type: (str, str, any) -> None
    node = DefaultValueNode(name=name, longName=longName)
    return node


def createConnectionValidityNode(name, longName):
    # type: (str, str) -> ConnectionValidityNode

    node = ConnectionValidityNode(name=name, longName=longName)

    return node


def saveValidatorsToFile(validators, filepath):
    # type: (list, str) -> bool
    validatorDataList = list()
    for eachValidator in validators:
        validatorDataList.append(eachValidator.toData())

    c_parser.write(filepath=filepath, data=validatorDataList)

    return True


def updateNodeValuesFromDCC(node):
    #type: (c_nodes.Node) -> bool
    nodeType = node.nodeType
    if vr_insideDCC.insideMaya():
        from validateRig.core.maya import plugs as vrcm_plugs

        if nodeType == c_serialization.NT_DEFAULTVALUE:
            logger.info("Updating defaultValueNode value from Maya")
            data = node.defaultValueData
            attrName = data.keys()[0]
            mPlug = vrcm_plugs.getMPlugFromLongName(node.longName, attrName)
            value = vrcm_plugs.getMPlugValue(mPlug)
            logger.info("MayaName: %s MayaValue: %s" % (mPlug.name(), value))
            newData = {attrName: value}

            node.defaultValueData = newData

        elif nodeType == c_serialization.NT_CONNECTIONVALIDITY:
            logger.info("Updating connectionNode value from Maya")
            data = node.connectionData
            srcData = data.get("srcData", list())
            srcPlugData = srcData.get("plugData", list())
            srcNodeName = node.parent.longName
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(srcNodeName, srcPlugData)
            srcValue = vrcm_plugs.getMPlugValue(srcMPlug)
            logger.info("MayaName: %s MayaValue: %s" % (srcMPlug.name(), srcValue))
            srcData["attrValue"] = srcValue

            destData = data.get("destData", list())
            destPlugData = destData.get("plugData", list())
            destNodeName = node.longName
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)
            destValue = vrcm_plugs.getMPlugValue(destMPlug)
            logger.info("MayaName: %s MayaValue: %s" % (destMPlug.name(), destValue))
            destData["attrValue"] = destValue

            node.connectionData = data

    return False


def getNSFromSelectedInDCC(nameSpaceInput):
    """ App sends signal to this to get the namespace from the DCC """
    if vr_insideDCC.insideMaya():
        from maya import cmds
        # Smelly find of NS from : in name.
        firstSelected = cmds.ls(sl=True)[0]
        if ":" in firstSelected:
            ns = cmds.ls(sl=True)[0].split(":")[0]
            logger.debug("NS in DCC: %s" % ns)
            nameSpaceInput.setText(ns)


def selectNodesInDCC(nodeNames, event):
    # type: (list[str], QEvent) -> None

    for eachNode in nodeNames:
        if vr_insideDCC.insideMaya():
            from maya import cmds
            modifier = event.modifiers()
            if modifier == QtCore.Qt.ControlModifier:
                cmds.select(eachNode, add=True)
            else:
                cmds.select(eachNode, r=True)


def processValidationTreeWidgetDropEvent(nodeNames, validator, parent=None):
    # type: (list[str], c_validator.Validator, QtWidgets.QWidget) -> uid_attributeList.MultiSourceNodeListWidgets
    attrWidget = uied_validityNodeWidgets.MultiSourceNodeListWidgets("SourceNodes", parent)

    # Check to see if this exists in the validator we dropped over.
    for longNodeName in nodeNames:
        existingSourceNode = None
        if validator().sourceNodeLongNameExists(longNodeName):
            existingSourceNode = validator().findSourceNodeByLongName(longNodeName)


        srcNodesWidget = None
        if vr_insideDCC.insideMaya():
            from validateRig.core.maya import validityNodeListWidget as vrcm_validityNodeListWidget
            if existingSourceNode is None:
                srcNodesWidget = vrcm_validityNodeListWidget.MayaValidityNodesSelector(longNodeName=longNodeName, parent=None)
            else:
                srcNodesWidget = vrcm_validityNodeListWidget.MayaValidityNodesSelector.fromSourceNode(sourceNode=existingSourceNode, parent=None)

        if srcNodesWidget is None:
            continue

        attrWidget.addListWidget(srcNodesWidget)
        attrWidget.sourceNodesAccepted.connect(partial(validator().addSourceNodes, force=True))

    return attrWidget
