#  Copyright (c) 2020.  James Dunlop
import logging
from const import serialization as c_serialization
from const import constants as vrc_constants
from core.maya import utils as cm_utils
from core.maya import plugs as cm_plugs
import maya.api.OpenMaya as om2
logger = logging.getLogger(__name__)

##############################################
# VALIDATE
def validateValidatorSourceNodes(validator):
    # type: (Validator) -> None
    validator.status = vrc_constants.NODE_VALIDATION_PASSED
    for eachSourceNode in validator.iterSourceNodes():
        eachSourceNode.status = vrc_constants.NODE_VALIDATION_PASSED
        srcNodeName = eachSourceNode.longName
        if not cm_utils.exists(srcNodeName):
            continue

        defaultStatus = __validateDefaultNodes(eachSourceNode)
        connectionStatus = __validateConnectionNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if not passed:
            eachSourceNode.status = vrc_constants.NODE_VALIDATION_FAILED
            validator.status = vrc_constants.NODE_VALIDATION_FAILED


def __validateDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        logger.info("Checking defaultValue for: {}".format(eachValidationNode.displayName))
        defaultNodeLongName = eachValidationNode.longName
        defaultAttrName = eachValidationNode.name
        defaultNodeValue = eachValidationNode.defaultValue

        attrValue = cm_utils.getAttrValue(defaultNodeLongName, defaultAttrName)
        result = defaultNodeValue == attrValue
        if not setValidationStatus(eachValidationNode, result):
            passed = False
        logger.info("\tresult: {}".format(result))

    return passed


def __validateConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue

        logger.info("Checking connections for: {}".format(eachValidationNode.displayName))
        srcMPlug = cm_plugs.getMPlugFromLongName(sourceNode.longName, eachValidationNode.srcAttrName)
        destMPlug = cm_plugs.getMPlugFromLongName(eachValidationNode.longName, eachValidationNode.destAttrName)
        if eachValidationNode.srcAttrIsIndexed:
            idx = eachValidationNode.srcAttrIndex
            if srcMPlug.isArray:
                srcMPlug = srcMPlug.elementByLogicalIndex(idx)
            else:
                srcMPlug = srcMPlug.child(idx)

        if eachValidationNode.destAttrIsIndexed:
            idx = eachValidationNode.destAttrIndex
            if destMPlug.isArray:
                destMPlug = destMPlug.elementByLogicalIndex(idx)
            else:
                destMPlug = destMPlug.child(idx)

        conns = destMPlug.connectedTo(True, False)
        if not conns:
            result = False
        else:
            result = conns[0] == srcMPlug

        if not setValidationStatus(eachValidationNode, result):
            passed = False

    return passed


##############################################
# REPAIR
def repairValidatorSourceNodes(validator):
    # type: (Validator) -> None
    for eachSourceNode in validator.iterSourceNodes():
        srcNodeName = eachSourceNode.longName
        if not cm_utils.exists(srcNodeName):
            continue

        defaultStatus = __repairDefaultNodes(eachSourceNode)
        connectionStatus = __repairConnectionNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if passed:
            validator.status = vrc_constants.NODE_VALIDATION_FAILED
        else:
            validator.status = vrc_constants.NODE_VALIDATION_PASSED


def __repairDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.status == vrc_constants.NODE_VALIDATION_PASSED:
            continue
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        # sourceAttrName = eachValidationNode.longName
        # defaultValue = eachValidationNode.defaultValue
        # if isinstance(defaultValue, list):
        #     cmds.setAttr(
        #         sourceAttrName, defaultValue[0], defaultValue[1], defaultValue[2]
        #     )
        # else:
        #     cmds.setAttr(sourceAttrName, eachValidationNode.defaultValue)
        # TODO om2

        setValidationStatus(eachValidationNode, True)

    return True


def __repairConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool
    mDagMod = om2.MDagModifier()

    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue
        if eachValidationNode.status == vrc_constants.NODE_VALIDATION_PASSED:
            continue

        srcMPlug = cm_plugs.getMPlugFromLongName(sourceNode.longName, eachValidationNode.srcAttrName)
        destMPlug = cm_plugs.getMPlugFromLongName(eachValidationNode.longName, eachValidationNode.destAttrName)
        if eachValidationNode.srcAttrIsIndexed:
            idx = eachValidationNode.srcAttrIndex
            if srcMPlug.isArray:
                srcMPlug = srcMPlug.elementByLogicalIndex(idx)
            else:
                srcMPlug = srcMPlug.child(idx)

        if eachValidationNode.destAttrIsIndexed:
            idx = eachValidationNode.destAttrIndex
            if destMPlug.isArray:
                destMPlug = destMPlug.elementByLogicalIndex(idx)
            else:
                destMPlug = destMPlug.child(idx)

        mDagMod.connect(srcMPlug, destMPlug)
        setValidationStatus(eachValidationNode, True)

    mDagMod.doIt()

    return True


def setValidationStatus(validationNode, result):
    # type: (ValidationNode, bool) -> bool
    if result:
        validationNode.status = vrc_constants.NODE_VALIDATION_PASSED
        return result

    validationNode.status = vrc_constants.NODE_VALIDATION_FAILED
    return result
