#  Copyright (c) 2020.  James Dunlop
import logging
from const import serialization as c_serialization
from const import constants as vrc_constants
from core.maya import utils as cm_utils
from core.maya import plugs as cm_plugs
from core.maya import types as cm_types
reload(cm_plugs)
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

        logger.info(
            "Checking defaultValue for: {}".format(eachValidationNode.displayName)
        )
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
    GETATTR_IGNORESTYPES = (cm_types.MESSAGE, cm_types.MATRIXF44)
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue

        logger.info(
            "Checking connections for: {}".format(eachValidationNode.displayName)
        )
        srcMPlug = cm_plugs.getMPlugFromLongName(
            sourceNode.longName, eachValidationNode.srcAttrName
        )
        destMPlug = cm_plugs.getMPlugFromLongName(
            eachValidationNode.longName, eachValidationNode.destAttrName
        )
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

        result = False
        if conns:
            result = conns[0] == srcMPlug

        if not setValidationStatus(eachValidationNode, result):
            passed = False

        resultSrcValue = True
        srcPlugType = cm_plugs.getMPlugType(srcMPlug)
        if srcPlugType not in GETATTR_IGNORESTYPES:
            srcAttrValue = cm_plugs.getMPlugValue(srcMPlug)
            resultSrcValue = eachValidationNode.srcAttrValue == srcAttrValue

        result = all((result, resultSrcValue))
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

        mSel = om2.MSelectionList()
        mSel.add(eachValidationNode.longName)
        mFn = om2.MFnDependencyNode(mSel.getDependNode(0))
        srcMPlug = mFn.findPlug(eachValidationNode.name, False)

        defaultValue = eachValidationNode.defaultValue
        cm_plugs.setMPlugValue(srcMPlug, defaultValue)

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

        srcMPlug = cm_plugs.getMPlugFromLongName(
            sourceNode.longName, eachValidationNode.srcAttrName
        )
        destMPlug = cm_plugs.getMPlugFromLongName(
            eachValidationNode.longName, eachValidationNode.destAttrName
        )
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

        srcValue = eachValidationNode.srcAttrValue
        cm_plugs.setMPlugValue(srcMPlug, srcValue)

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
