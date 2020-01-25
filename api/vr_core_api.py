#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtWidgets, QtCore, QtGui
import validateRig.inside as c_inside
from validateRig.core import validator as c_validator
from validateRig.core import parser as c_parser
from validateRig.core import factory as c_factory
from validateRig.core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode
from validateRig.const import serialization as c_serialization
from validateRig.uiElements.dialogs import attributeList as uid_attributeList

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


def createConnectionValidityNode(
    name, longName,
):
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
    print(node)


def getNSFromSelectedInDCC(nameSpaceInput):
    """ App sends signal to this to get the namespace from the DCC """
    if c_inside.insideMaya():
        from maya import cmds
        # Smelly find of NS from : in name.
        firstSelected = cmds.ls(sl=True)[0]
        if ":" in firstSelected:
            ns = cmds.ls(sl=True)[0].split(":")[0]
            logger.info("NS in DCC: %s" % ns)
            nameSpaceInput.setText(ns)


def selectNodesInDCC(nodeNames, event):
    for eachNode in nodeNames:
        if c_inside.insideMaya():
            from maya import cmds
            modifier = event.modifiers()
            if modifier == QtCore.Qt.ControlModifier:
                cmds.select(eachNode, add=True)
            else:
                cmds.select(eachNode, r=True)


def processValidationTreeWidgetDropEvent(nodeNames, validator, parent=None):
    # type: (list, Validator, QtWidgets.QWidget) -> None
    attrWidget = uid_attributeList.MultiSourceNodeListWidgets("SourceNodes", parent)

    # Check to see if this exists in the validator we dropped over.
    for longNodeName in nodeNames:
        if not validator().sourceNodeLongNameExists(longNodeName):
            logger.info("Creating new sourceNode.")
            srcNodesWidget = uid_attributeList.MayaValidityNodesSelector(longNodeName=longNodeName, parent=None)

        else:
            logger.info("SourceNode: {} exists!".format(longNodeName))
            existingSourceNode = validator().findSourceNodeByLongName(longNodeName)
            srcNodesWidget = uid_attributeList.MayaValidityNodesSelector.fromSourceNode(sourceNode=existingSourceNode, parent=None)

        if srcNodesWidget is None:
            continue

        attrWidget.addListWidget(srcNodesWidget)

    return attrWidget
