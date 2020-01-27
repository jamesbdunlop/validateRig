#  Copyright (c) 2020.  James Dunlop
import logging
from validateRig.const import serialization as c_serialization
from validateRig.const import constants as vrconst_constants
from validateRig.core.maya import utils as cm_utils
from validateRig.core.maya import plugs as cm_plugs
from validateRig.core.maya import types as cm_types

import maya.api.OpenMaya as om2

logger = logging.getLogger(__name__)

##############################################
# VALIDATE
def validateValidatorSourceNodes(validator):
    # type: (Validator) -> None

    validator.status = vrconst_constants.NODE_VALIDATION_PASSED
    for eachSourceNode in validator.iterSourceNodes():
        eachSourceNode.status = vrconst_constants.NODE_VALIDATION_PASSED
        srcNodeName = eachSourceNode.longName
        if not cm_utils.exists(srcNodeName):
            continue

        defaultStatus = __validateDefaultNodes(eachSourceNode)
        connectionStatus = __validateConnectionNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if not passed:
            eachSourceNode.status = vrconst_constants.NODE_VALIDATION_FAILED
            validator.status = vrconst_constants.NODE_VALIDATION_FAILED


def __validateDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool

    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        data = eachValidationNode.defaultValueData
        defaultNodeLongName = eachValidationNode.longName
        logger.debug("defaultNodeLongName: %s" % defaultNodeLongName)
        for dvName, dvValue in data.iteritems():
            logger.debug("dvName: %s" % dvName)
            attrValue = cm_utils.getAttrValue(defaultNodeLongName, dvName)
            result = dvValue == attrValue
            if not setValidationStatus(eachValidationNode, result):
                passed = False

    return passed


def fetchMPlugFromConnectionData(nodeLongName, plugData):
    copyPlugData = plugData[:]
    mPlug = None

    logger.debug("-----------fetchMPlugFromConnectionData-------------")
    logger.debug("\t-- %s" % plugData)
    while copyPlugData:
        plgIsElement, plgIsChild, plgPlugName, plgIndex = copyPlugData[-1]
        logger.debug("\t%-- s %s %s %s" % (plgIsElement, plgIsChild, plgPlugName, plgIndex))

        if mPlug is None:
            mPlug = cm_plugs.getMPlugFromLongName(nodeLongName, plgPlugName)
            if plgIsElement:
                mPlug = mPlug.elementByLogicalIndex(plgIndex)
            elif plgIsChild:
                mPlug = mPlug.child(plgIndex)
            logger.debug("\tFound starting plug: %s" % (mPlug.name()))

        elif plgIsElement:
            logger.debug("\t\t%s IsElement" % (plgPlugName))
            logger.debug("\t\tparentPlug: %s" % (mPlug.name()))
            mPlug = mPlug.elementByLogicalIndex(plgIndex)
            logger.debug("\t\tnewPlug: %s" % (mPlug.name()))

        elif plgIsChild:
            logger.debug("\t\t%s IsChild" % (plgPlugName))
            logger.debug("\t\tparentPlug: %s" % (mPlug.name()))
            mPlug = mPlug.child(plgIndex)
            logger.debug("\t\tnewPlug: %s" % (mPlug.name()))

        copyPlugData.pop()

    logger.debug("FINAL PLUG %s" % mPlug.name())
    return mPlug


def __validateConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool

    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue

        data = eachValidationNode.connectionData
        srcData = data.get("srcData", None)
        destData = data.get("destData", None)
        srcAttrName = srcData.get("attrName", None)
        srcAttrValue = srcData.get("attrValue", None)
        srcPlugData = srcData.get("plugData", None)

        srcIsElement, srcIsChild, srcPlugName, _ = srcPlugData[0]
        isSrcIndexed = False
        if srcIsElement or srcIsChild:
            isSrcIndexed = True
        if not isSrcIndexed:
            srcMPlug = cm_plugs.getMPlugFromLongName(sourceNode.longName, srcAttrName)
        else:
            srcMPlug = fetchMPlugFromConnectionData(sourceNode.longName, srcPlugData)

        destNodeName = destData.get("nodeName", None)
        destAttrValue = destData.get("attrValue", None)
        destPlugData = destData.get("plugData", None)

        destIsElement, destIsChild, destPlugName, _ = destPlugData[0]
        isDestIndexed = False
        if destIsElement or destIsChild:
            isDestIndexed = True
        if not isDestIndexed:
            destMPlug = cm_plugs.getMPlugFromLongName(destNodeName, destPlugName)
        else:
            destMPlug = fetchMPlugFromConnectionData(destNodeName, destPlugData)

        conns = destMPlug.connectedTo(True, False)
        result = False
        if conns:
            result = conns[0] == srcMPlug

        if not setValidationStatus(eachValidationNode, result):
            logger.debug("NOT CONNECTED %s %s " % (srcMPlug.name(), destMPlug.name()))
            passed = False

        # DEFAULT VALUES OF THE SRC ATTR NOW AS WE CULL DEFAULT VALUE NODES IF THEY'RE ALREADY CONNECTION ATTRS
        resultSrcValue = True
        srcPlugType = cm_plugs.getMPlugType(srcMPlug)
        GETATTR_IGNORESTYPES = (cm_types.MESSAGE, cm_types.MATRIXF44)
        if srcPlugType not in GETATTR_IGNORESTYPES:
            currentSrcAttrValue = cm_plugs.getMPlugValue(srcMPlug)
            resultSrcValue = srcAttrValue == currentSrcAttrValue

        resultDestValue = True
        destPlugType = cm_plugs.getMPlugType(destMPlug)
        GETATTR_IGNORESTYPES = (cm_types.MESSAGE, cm_types.MATRIXF44)
        if destPlugType not in GETATTR_IGNORESTYPES:
            currentDestAttrValue = cm_plugs.getMPlugValue(destMPlug)
            resultDestValue = destAttrValue == currentDestAttrValue

        result = all((result, resultSrcValue, resultDestValue))
        if not setValidationStatus(eachValidationNode, result):
            logger.debug("NOT AT DEFAULT VALUE %s %s " % (srcMPlug.name(), destMPlug.name()))
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
            validator.status = vrconst_constants.NODE_VALIDATION_FAILED
        else:
            validator.status = vrconst_constants.NODE_VALIDATION_PASSED


def __repairDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool

    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.status == vrconst_constants.NODE_VALIDATION_PASSED:
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
        if eachValidationNode.status == vrconst_constants.NODE_VALIDATION_PASSED:
            continue

        data = eachValidationNode.connectionData
        srcData = data.get("srcData", None)
        srcAttrValue = srcData.get("attrName", None)
        srcAttrName = srcData.get("attrValue", None)
        srcPlugData = srcData.get("plugData", None)

        destData = data.get("destData", None)
        destNodeName = destData.get("nodeName", None)
        destPlugData = destData.get("plugData", None)

        ############################################################
        srcIsElement, srcIsChild, srcPlugName, _ = srcPlugData[0]
        if srcIsElement or srcIsChild:
            srcMPlug = fetchMPlugFromConnectionData(eachValidationNode.longName, srcPlugData)

        else:
            srcMPlug = cm_plugs.getMPlugFromLongName(eachValidationNode.longName, srcAttrName)

        ############################################################
        destIsElement, destIsChild, destPlugName, _ = destPlugData[0]
        if destIsElement or destIsChild:
            destMPlug = fetchMPlugFromConnectionData(destNodeName, destPlugData)

        else:
            destMPlug = cm_plugs.getMPlugFromLongName(destNodeName, destPlugName)

        mDagMod.connect(srcMPlug, destMPlug)
        cm_plugs.setMPlugValue(srcMPlug, srcAttrValue)
        setValidationStatus(eachValidationNode, True)

    mDagMod.doIt()

    return True


def setValidationStatus(validationNode, result):
    # type: (ValidationNode, bool) -> bool

    if result:
        validationNode.status = vrconst_constants.NODE_VALIDATION_PASSED
        return result

    validationNode.status = vrconst_constants.NODE_VALIDATION_FAILED
    return result
