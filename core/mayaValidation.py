# Copyright (c) 2019.  James Dunlop
import logging
from core import inside
if inside.insideMaya():
    from maya import cmds
from vrConst import serialization as c_serialization
from vrConst import constants as vrc_constants
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

def validateSourceNodes(validator):
    # type: (Validator) -> None
    validator.status = vrc_constants.NODE_VALIDATION_PASSED
    for eachSourceNode in validator.iterSourceNodes():
        srcNodeName = eachSourceNode.longName
        if not exists(srcNodeName):
            continue

        for eachValidationNode in eachSourceNode.iterDescendants():
            passed = False
            if eachValidationNode.nodeType == c_serialization.NT_DEFAULTVALUE:
                attrName = "{}.{}".format(srcNodeName, eachValidationNode.name)
                passed = eachValidationNode.defaultValue == cmds.getAttr(attrName)

            elif eachValidationNode.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                destAttrName = "{}.{}".format(eachValidationNode.longName, eachValidationNode.destAttrName)
                passed = cmds.isConnected(srcNodeName, destAttrName)

            if passed:
                eachValidationNode.status = vrc_constants.NODE_VALIDATION_PASSED
            else:
                eachValidationNode.status = vrc_constants.NODE_VALIDATION_FAILED
                validator.status = vrc_constants.NODE_VALIDATION_FAILED

def repairSourceNodes(validator):
    # type: (Validator) -> None
    for eachSourceNode in validator.iterSourceNodes():
        srcNodeName = eachSourceNode.longName
        if not exists(srcNodeName):
            continue

        for eachValidationNode in eachSourceNode.iterDescendants():
            if eachValidationNode.status == vrc_constants.NODE_VALIDATION_PASSED:
                continue

            if eachValidationNode.nodeType == c_serialization.NT_DEFAULTVALUE:
                attrName = "{}.{}".format(srcNodeName, eachValidationNode.name)

                cmds.setAttr(attrName,  eachValidationNode.defaultValue[0]) # TODO handling this crap properly
                eachValidationNode.status = vrc_constants.NODE_VALIDATION_PASSED

            elif eachValidationNode.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                destAttrName = "{}.{}".format(eachValidationNode.longName, eachValidationNode.destAttrName)
                cmds.connectAttr(srcNodeName, destAttrName, f=True)
                eachValidationNode.status = vrc_constants.NODE_VALIDATION_PASSED

    validator.status = vrc_constants.NODE_VALIDATION_PASSED
