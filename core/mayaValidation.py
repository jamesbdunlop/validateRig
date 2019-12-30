#  Copyright (c) 2019.  James Dunlop
# pragma: no cover
import logging
from core import inside
if inside.insideMaya():
    from maya import cmds
from const import serialization as c_serialization
from const import constants as vrc_constants
logger = logging.getLogger(__name__)


def getPlugValue(mplug):
    """
    :param mplug: MPlug
    :return: The value of the passed in MPlug or None
    """
    import maya.api.OpenMaya as om2

    pAttribute = mplug.attribute()
    apiType = pAttribute.apiType()

    # Float Groups - rotate, translate, scale; Com2pounds
    if apiType in [
        om2.MFn.kAttribute3Double,
        om2.MFn.kAttribute3Float,
        om2.MFn.kCompoundAttribute,
    ]:
        result = []
        if mplug.isCompound:
            for c in range(mplug.numChildren()):
                result.append(getPlugValue(mplug.child(c)))
            return result

    # Distance
    elif apiType in [om2.MFn.kDoubleLinearAttribute, om2.MFn.kFloatLinearAttribute]:
        return mplug.asMDistance().asCentimeters()

    # Angle
    elif apiType in [om2.MFn.kDoubleAngleAttribute, om2.MFn.kFloatAngleAttribute]:
        return mplug.asMAngle().asDegrees()

    # TYPED
    elif apiType == om2.MFn.kTypedAttribute:
        pType = om2.MFnTypedAttribute(pAttribute).attrType()
        # Matrix
        if pType == om2.MFnData.kMatrix:
            return om2.MFnMatrixData(mplug.asMObject()).matrix()
        # String
        elif pType == om2.MFnData.kString:
            return mplug.asString()

    # MATRIX
    elif apiType == om2.MFn.kMatrixAttribute:
        return om2.MFnMatrixData(mplug.asMObject()).matrix()

    # NUMBERS
    elif apiType == om2.MFn.kNumericAttribute:
        pType = om2.MFnNumericAttribute(pAttribute).numericType()
        if pType == om2.MFnNumericData.kBoolean:
            return mplug.asBool()
        elif pType in [
            om2.MFnNumericData.kShort,
            om2.MFnNumericData.kInt,
            om2.MFnNumericData.kLong,
            om2.MFnNumericData.kByte,
        ]:
            return mplug.asInt()
        elif pType in [
            om2.MFnNumericData.kFloat,
            om2.MFnNumericData.kDouble,
            om2.MFnNumericData.kAddr,
        ]:
            return mplug.asDouble()

    # Enum
    elif apiType == om2.MFn.kEnumAttribute:
        return mplug.asInt()

def exists(srcNodeName):
    if not cmds.objExists(srcNodeName):
        logger.error("Failed to find sourceNode %s in scene!" % srcNodeName)
        return False
    return True

### VALIDATE
def validateValidatorSourceNodes(validator):
    # type: (Validator) -> None
    validator.status = vrc_constants.NODE_VALIDATION_FAILED
    for eachSourceNode in validator.iterSourceNodes():
        srcNodeName = eachSourceNode.longName
        if not exists(srcNodeName):
            continue
        defaultStatus = validateDefaultNodes(eachSourceNode)
        connectionStatus = validateConnectionNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if passed:
            validator.status = vrc_constants.NODE_VALIDATION_PASSED

def validateDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        attrName = "{}.{}".format(sourceNode.longName, eachValidationNode.name)
        result = eachValidationNode.defaultValue == cmds.getAttr(attrName)
        if not setValidationStatus(eachValidationNode, result):
            passed = False

    return passed

def validateConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue

        result = cmds.isConnected(sourceNode.longName, eachValidationNode.longName)
        if not setValidationStatus(eachValidationNode, result):
            passed = False

    return passed

### REPAIR
def repairValidatorSourceNodes(validator):
    # type: (Validator) -> None
    for eachSourceNode in validator.iterSourceNodes():
        srcNodeName = eachSourceNode.longName
        if not exists(srcNodeName):
            continue

        defaultStatus = repairDefaultNodes(eachSourceNode)
        connectionStatus = repairDefaultNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if passed:
            validator.status = vrc_constants.NODE_VALIDATION_FAILED

def repairDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.status == vrc_constants.NODE_VALIDATION_PASSED:
            continue
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        # TODO handling this crap properly
        attrName = "{}.{}".format(sourceNode.longName, eachValidationNode.name)
        cmds.setAttr(attrName, eachValidationNode.defaultValue[0])
        setValidationStatus(eachValidationNode, True)

    return True

def repairConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue

        cmds.connectAttr(sourceNode.name, eachValidationNode.longName, force=True)
        setValidationStatus(eachValidationNode, True)

    return True

def setValidationStatus(validationNode, result):
    # type: (ValidationNode, bool) -> bool
    if result:
        validationNode.status = vrc_constants.NODE_VALIDATION_PASSED
        return result

    validationNode.status = vrc_constants.NODE_VALIDATION_FAILED
    return result
