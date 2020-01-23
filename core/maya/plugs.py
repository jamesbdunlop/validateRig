#  Copyright (c) 2019.  James Dunlop
# pragma: no cover
import logging
import maya.api.OpenMaya as om2
from core.maya import types as cm_types

logger = logging.getLogger(__name__)


def getMPlugValue(mplug):
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
                result.append(getMPlugValue(mplug.child(c)))
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


def getMPlugType(mplug):
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
                result.append(getMPlugType(mplug.child(c)))
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
        return cm_types.MESSAGE


def setMPlugValue(mplug, value):
    plugType = getMPlugType(mplug)
    status = False
    if plugType == "message":
        return

    pAttribute = mplug.attribute()
    apiType = pAttribute.apiType()
    if apiType in [om2.MFn.kAttribute3Double, om2.MFn.kAttribute3Float, om2.MFn.kCompoundAttribute]:
        if mplug.isCompound:
            for x in range(mplug.numChildren()):
                if not mplug.child(x).isConnected:
                    mplug.child(x).setFloat(value[x])

    elif plugType == cm_types.FLOAT:
        mplug.setFloat(value)
        status = True

    elif plugType == cm_types.MATRIXF44:
        pass
        # mplug.setMatrix(value)
        # status = True

    elif plugType == cm_types.INT:
        mplug.setInt(value)
        status = True

    elif plugType == cm_types.BOOL:
        mplug.setBool(value)
        status = True

    elif plugType == cm_types.DOUBLE:
        mplug.setDouble(value)
        status = True

    return status


def getMPlugFromLongName(nodeLongName, plugName):
    # type: (str, str) -> om2.MPlug
    if isinstance(plugName, list):
        plugName = plugName[0]
    mSel = om2.MSelectionList()
    mSel.add(str(nodeLongName))
    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)

    mplug = mFn.findPlug(plugName, False)

    return mplug


def getMPlugElementFromLongName(nodeLongName, plugName, index, useLogicalIndex=True):
    # type: (str, str, int, bool) -> om2.MPlug
    parentPlug = getMPlugFromLongName(nodeLongName, plugName)
    if parentPlug.isArray():
        mplug = getMPlugArrayElement(parentPlug, index, useLogicalIndex=useLogicalIndex)

        return mplug


def getMPlugArrayElement(mplug, index, useLogicalIndex=True):
    # type: (om2.MPlug, int, bool) -> om2.MPlug
    if useLogicalIndex:
        mplug = mplug.elementyByLogicalIndex(index)
    else:
        mplug = mplug.elementByPhysicalIndex(index)

    return mplug


def getMPlugChildFromLongName(nodeLongName, plugName, index):
    # type: (str, str, int) -> om2.MPlug
    parentPlug = getMPlugFromLongName(nodeLongName, plugName)
    if parentPlug.isCompound:
        mplug = parentPlug.child(index)

        return mplug


def isMPlugIndexed(mPlug):
    isElement = mPlug.isElement
    isChild = mPlug.isChild
    isIndexed = any((isElement, isChild))

    return isIndexed


def fetchIndexedPlugData(mplug, plgData=None):
    # type: (om2.MPlug, list) -> list
    """
    builds a list of the hrc of the plug. the last is the list is the first plug in the hrc.
    eg:
        plgData = [[False, True, u'cvs[0]', 0], [True, False, u'jd_hermiteArrayCrv1.cvs', None]]
        plgData = [isElement, isChild, plugName, plgIdx], [isElement, isChild, plugName, plgIdx]]
    """
    isIndexedMPlug = isMPlugIndexed(mplug)
    if plgData is None:
        plgData = list()

    currentPlug = [None] * 4
    if isIndexedMPlug and mplug.isElement:
        # partialName(includeNodeName=False, includeNonMandatoryIndices=False,
        # includeInstancedIndices=False, useAlias=False, useFullAttributePath=False,
        # useLongNames=False)
        parentPlug = om2.MPlug(mplug.node(), mplug.attribute())
        for x in range(parentPlug.numElements()):
            if parentPlug.elementByLogicalIndex(x) == mplug:
                currentPlug[3] = x
        currentPlug[2] = mplug.partialName(False, False, False, False, True, True)

    elif mplug.isChild:
        parentPlug = mplug.parent()
        # partialName(includeNodeName=False, includeNonMandatoryIndices=False,
        # includeInstancedIndices=False, useAlias=False, useFullAttributePath=False,
        # useLongNames=False)
        currentPlug[2] = parentPlug.partialName(False, False, False, False, True, True)
        for x in range(parentPlug.numChildren()):
            if parentPlug.child(x) == mplug:
                currentPlug[3] = x

    else:
        currentPlug[2] = mplug.partialName(False, False, False, False, True, True)
        currentPlug[3] = None

    currentPlug[0] = mplug.isElement
    currentPlug[1] = mplug.isChild
    plgData.append(currentPlug)

    if currentPlug[1] and isMPlugIndexed(parentPlug):
        fetchIndexedPlugData(parentPlug, plgData)

    return plgData
