#  Copyright (C) Animal Logic Pty Ltd. All rights reserved.
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
        logger.debug("Validating sourceNode: %s" % eachSourceNode.longName)
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
        logger.debug("defaultNodeLongName: %s" % defaultNodeLongName)
        dvAttrName = data.keys()[0]
        logger.debug("dvName: %s" % dvAttrName)

        dvValue = data.values()[0]
        logger.debug("dvValue: %s" % dvValue)

        dvMPlug = vrcm_plugs.getMPlugFromLongName(defaultNodeLongName, dvAttrName)
        dvMPlugType = vrcm_plugs.getMPlugType(dvMPlug)
        dvMPlugValue = vrcm_plugs.getMPlugValue(dvMPlug)
        logger.debug("dvMPlugType: %s" % dvMPlugType)
        logger.debug("dvMPlugValue: %s" % dvMPlugValue)
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
        # {'destData': {'attrValue'   : 0.0,
        #               'nodeLongName': u':testRigNamespace:jd_hermiteArrayCrv1',
        #               'nodeName'    : u'testRigNamespace:jd_hermiteArrayCrv1',
        #               'plugData'    : [[False, True, u'inTangentWeight', 0],
        #                                [True, False, u'cvs', 0]]},
        #  'srcData' : {'attrName'    : u'translateX',
        #               'attrValue'   : 0.0,
        #               'nodeLongName': u'|myChar|rig|testRigNamespace:mycharName_hrc|testRigNamespace:rig'
        #                               u'|testRigNamespace:control_layer|testRigNamespace:master_ctrl_srtBuffer'
        #                               u'|testRigNamespace:body_ctrl',
        #               'plugData'    : [[False, True, u'translateX', 0],
        #                                [False, False, u'translate', None]]}}
        connectionData = eachValidationNode.connectionData

        srcData = connectionData.get("srcData", None)
        srcAttrName = srcData.get("attrName", None)
        srcAttrLongName = srcData.get("nodeLongName", None)
        srcAttrValue = srcData.get("attrValue", None)
        srcPlugData = srcData.get("plugData", None)
        logger.debug("srcAttrName: %s" % srcAttrName)
        logger.debug("srcAttrValue: %s" % srcAttrValue)
        logger.debug("srcAttrLongName: %s" % srcAttrLongName)
        logger.debug("srcPlugData: %s" % srcPlugData)

        srcIsElement, srcIsChild, srcPlugName, _ = srcPlugData[0]
        isSrcArrayOrCompound = srcIsElement or srcIsChild
        logger.debug("isSrcArrayOrCompound: %s" % isSrcArrayOrCompound)
        if isSrcArrayOrCompound:
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(sourceNode.longName, srcPlugData)
        else:
            srcMPlug = vrcm_plugs.getMPlugFromLongName(sourceNode.longName, srcAttrName)

        destData = connectionData.get("destData", None)
        destNodeName = destData.get("nodeLongName", None)
        destAttrValue = destData.get("attrValue", None)
        destPlugData = destData.get("plugData", None)
        logger.debug("destNodeName: %s" % destNodeName)
        logger.debug("destAttrValue: %s" % destAttrValue)
        logger.debug("destPlugData: %s" % destPlugData)

        destIsElement, destIsChild, destPlugName, _ = destPlugData[0]
        isDestArrayOrCompound = destIsElement or destIsChild
        logger.debug("isDestArrayOrCompound: %s" % isDestArrayOrCompound)
        if isDestArrayOrCompound:
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)
        else:
            destMPlug = vrcm_plugs.getMPlugFromLongName(destNodeName, destPlugName)

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
        srcAttrName = srcData.get("attrName", None)
        srcNodeName = srcData.get("nodeLongName", None)
        srcAttrValue = srcData.get("attrValue", None)
        srcPlugData = srcData.get("plugData", None)

        destData = data.get("destData", None)
        destNodeName = destData.get("nodeLongName", None)
        destPlugData = destData.get("plugData", None)

        ############################################################
        srcIsElement, srcIsChild, srcPlugName, _ = srcPlugData[0]
        if srcIsElement or srcIsChild:
            srcMPlug = vrcm_plugs.fetchMPlugFromConnectionData(srcNodeName, srcPlugData)

        else:
            srcMPlug = vrcm_plugs.getMPlugFromLongName(srcNodeName, srcAttrName)
        logger.debug("SrcPlugData: %s" % srcPlugData)
        logger.debug("srcMPlug: %s" % srcMPlug)

        ############################################################
        destIsElement, destIsChild, destPlugName, _ = destPlugData[0]
        logger.debug("destIsElement: %s" % destIsElement)
        logger.debug("destIsChild: %s" % destIsChild)
        logger.debug("destPlugName: %s" % destPlugName)

        if destIsElement or destIsChild:
            destMPlug = vrcm_plugs.fetchMPlugFromConnectionData(destNodeName, destPlugData)
        else:
            destMPlug = vrcm_plugs.getMPlugFromLongName(destNodeName, destPlugName)

        logger.debug("destPlugData: %s" % destPlugData)
        logger.debug("destMPlug: %s" % destMPlug)
        if not destMPlug.isDestination:
            mDagMod.connect(srcMPlug, destMPlug)

        # This may also be connected to. So we skip setting the default value for this plug.
        if not srcMPlug.isDestination:
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
