#  Copyright (c) 2020.  James Dunlop
import logging
from validateRig.const import serialization as c_serialization
from validateRig.const import constants as vrconst_constants
from validateRig.core.maya import utils as vrcm_utils
from validateRig.core.maya import plugs as vrcm_plugs
from validateRig.core.maya import types as vrcm_types

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
        if not vrcm_utils.exists(srcNodeName):
            logger.error("Missing node %s" % eachSourceNode.longName)
            eachSourceNode.status = vrconst_constants.NODE_VALIDATION_MISSINGSRC
            validator.status = vrconst_constants.NODE_VALIDATION_MISSINGSRC
            # Set all children to failed
            for eachChild in eachSourceNode.iterChildren():
                eachChild.status = vrconst_constants.NODE_VALIDATION_MISSINGSRC
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
        if not vrcm_utils.exists(eachValidationNode.longName):
            eachValidationNode.status = vrconst_constants.NODE_VALIDATION_MISSINGSRC
            continue

        data = eachValidationNode.defaultValueData
        defaultNodeLongName = eachValidationNode.longName
        logger.info("defaultNodeLongName: %s" % defaultNodeLongName)
        dvAttrName = data.keys()[0]
        logger.info("dvName: %s" % dvAttrName)

        dvValue = data.values()[0]
        logger.info("dvValue: %s" % dvValue)

        dvMPlug = vrcm_plugs.getMPlugFromLongName(defaultNodeLongName, dvAttrName)
        dvMPlugType = vrcm_plugs.getMPlugType(dvMPlug)
        dvMPlugValue = vrcm_plugs.getMPlugValue(dvMPlug)
        logger.info("dvMPlugType: %s" % dvMPlugType)
        logger.info("dvMPlugValue: %s" % dvMPlugValue)
        if dvMPlugType == vrcm_types.MATRIXF44:
            dvValue = om2.MMatrix((
                (dvValue[0], dvValue[1], dvValue[2], dvValue[3]),
                (dvValue[4], dvValue[5], dvValue[6], dvValue[7]),
                (dvValue[8], dvValue[9], dvValue[10], dvValue[11]),
                (dvValue[12], dvValue[13], dvValue[14], dvValue[15]),
                 ))
        result = dvValue == dvMPlugValue
        if not setValidationStatus(eachValidationNode, result):
            passed = False

    return passed


def __validateConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool

    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue
        if not vrcm_utils.exists(eachValidationNode.longName):
            eachValidationNode.status = vrconst_constants.NODE_VALIDATION_MISSINGDEST
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
            srcMPlug = vrcm_plugs.getMPlugFromLongName(sourceNode.longName, srcAttrName)
        else:
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(sourceNode.longName, srcPlugData)

        destNodeName = destData.get("nodeName", None)
        destAttrValue = destData.get("attrValue", None)
        destPlugData = destData.get("plugData", None)

        destIsElement, destIsChild, destPlugName, _ = destPlugData[0]
        isDestIndexed = False
        if destIsElement or destIsChild:
            isDestIndexed = True
        if not isDestIndexed:
            destMPlug = vrcm_plugs.getMPlugFromLongName(destNodeName, destPlugName)
        else:
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)

        conns = destMPlug.connectedTo(True, False)
        result = False
        if conns:
            result = conns[0] == srcMPlug

        if not setValidationStatus(eachValidationNode, result):
            logger.debug("NOT CONNECTED %s %s " % (srcMPlug.name(), destMPlug.name()))
            passed = False

        # DEFAULT VALUES OF THE SRC ATTR NOW AS WE CULL DEFAULT VALUE NODES IF THEY'RE ALREADY CONNECTION ATTRS
        resultSrcValue = True
        srcPlugType = vrcm_plugs.getMPlugType(srcMPlug)
        GETATTR_IGNORESTYPES = (vrcm_types.MESSAGE, vrcm_types.MATRIXF44)
        if srcPlugType not in GETATTR_IGNORESTYPES:
            currentSrcAttrValue = vrcm_plugs.getMPlugValue(srcMPlug)
            resultSrcValue = srcAttrValue == currentSrcAttrValue

        resultDestValue = True
        destPlugType = vrcm_plugs.getMPlugType(destMPlug)
        GETATTR_IGNORESTYPES = (vrcm_types.MESSAGE, vrcm_types.MATRIXF44)
        if destPlugType not in GETATTR_IGNORESTYPES:
            currentDestAttrValue = vrcm_plugs.getMPlugValue(destMPlug)
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
        if not vrcm_utils.exists(srcNodeName):
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
        # Exists check here
        mSel = om2.MSelectionList()
        mSel.add(eachValidationNode.longName)
        mFn = om2.MFnDependencyNode(mSel.getDependNode(0))
        srcMPlug = mFn.findPlug(eachValidationNode.name, False)

        data = eachValidationNode.defaultValueData
        defaultValue = data.values()[0]
        vrcm_plugs.setMPlugValue(srcMPlug, defaultValue)

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
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(eachValidationNode.longName, srcPlugData)

        else:
            srcMPlug = vrcm_plugs.getMPlugFromLongName(eachValidationNode.longName, srcAttrName)

        ############################################################
        destIsElement, destIsChild, destPlugName, _ = destPlugData[0]
        if destIsElement or destIsChild:
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)

        else:
            destMPlug = vrcm_plugs.getMPlugFromLongName(destNodeName, destPlugName)

        mDagMod.connect(srcMPlug, destMPlug)
        vrcm_plugs.setMPlugValue(srcMPlug, srcAttrValue)
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
