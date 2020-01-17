#  Copyright (c) 2019.  James Dunlop
# pragma: no cover
import logging
import maya.api.OpenMaya as om2
from core.maya import types as cm_types

logger = logging.getLogger(__name__)


def getPlugValue(mplug):
    # type: (MPlug) -> any

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


def getPlugType(mplug):
    # type: (MPlug) -> int
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
                result.append(getPlugType(mplug.child(c)))
            return result

    # Distance
    elif apiType in [om2.MFn.kDoubleLinearAttribute, om2.MFn.kFloatLinearAttribute]:
        return cm_types.FLOAT

    # Angle
    elif apiType in [om2.MFn.kDoubleAngleAttribute, om2.MFn.kFloatAngleAttribute]:
        return cm_types.FLOAT

    # TYPED
    elif apiType == om2.MFn.kTypedAttribute:
        pType = om2.MFnTypedAttribute(pAttribute).attrType()
        # Matrix
        if pType == om2.MFnData.kMatrix:
            return cm_types.MATRIXF44
        # String
        elif pType == om2.MFnData.kString:
            return cm_types.STRING

    # MATRIX
    elif apiType == om2.MFn.kMatrixAttribute:
        return cm_types.MATRIXF44

    # NUMBERS
    elif apiType == om2.MFn.kNumericAttribute:
        pType = om2.MFnNumericAttribute(pAttribute).numericType()
        if pType == om2.MFnNumericData.kBoolean:
            return cm_types.BOOL

        elif pType in [
            om2.MFnNumericData.kShort,
            om2.MFnNumericData.kInt,
            om2.MFnNumericData.kLong,
            om2.MFnNumericData.kByte,
        ]:
            return cm_types.INT

        elif pType in [
            om2.MFnNumericData.kFloat,
            om2.MFnNumericData.kDouble,
            om2.MFnNumericData.kAddr,
        ]:
            return cm_types.DOUBLE

    # Enum
    elif apiType == om2.MFn.kEnumAttribute:
        return cm_types.INT


    elif apiType == om2.MFn.kMessageAttribute:
        return None


def getPlugFromLongName(nodeLongName, attrName):
    # type: (str, str) -> om2.MPlug

    mSel = om2.MSelectionList()
    mSel.add(nodeLongName)
    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)

    plug = mFn.findPlug(attrName, False)

    return plug


def mPlugAsData(mplug):
    plugType = getPlugType(mplug)
    plugValue = getPlugValue(mplug)
    isArray = mplug.isArray()
    isCompound = mplug.isCompound()
    isElement = mplug.isElement()
    idx = None
    if isElement:
        idx = mplug.logicalIndex()

    data = {
        "plugType": plugType,
        "plugValue": plugValue
        }
