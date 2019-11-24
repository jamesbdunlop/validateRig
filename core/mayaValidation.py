# Copyright (c) 2019.  James Dunlop


def getPlugValue(self, plug):
    """
    :param plug: MPlug
    :return: The value of the passed in MPlug or None
    """
    # look to clean this up as this is my old MASSIVE plugValue..
    import maya.api.OpenMaya as om2

    pAttribute = plug.attribute()
    apiType = pAttribute.apiType()

    # Float Groups - rotate, translate, scale; Com2pounds
    if apiType in [
        om2.MFn.kAttribute3Double,
        om2.MFn.kAttribute3Float,
        om2.MFn.kCompoundAttribute,
    ]:
        result = []
        if plug.isCompound:
            for c in range(plug.numChildren()):
                result.append(self.getPlugValue(plug.child(c)))
            return result

    # Distance
    elif apiType in [om2.MFn.kDoubleLinearAttribute, om2.MFn.kFloatLinearAttribute]:
        return plug.asMDistance().asCentimeters()

    # Angle
    elif apiType in [om2.MFn.kDoubleAngleAttribute, om2.MFn.kFloatAngleAttribute]:
        return plug.asMAngle().asDegrees()

    # TYPED
    elif apiType == om2.MFn.kTypedAttribute:
        pType = om2.MFnTypedAttribute(pAttribute).attrType()
        # Matrix
        if pType == om2.MFnData.kMatrix:
            return om2.MFnMatrixData(plug.asMObject()).matrix()
        # String
        elif pType == om2.MFnData.kString:
            return plug.asString()

    # MATRIX
    elif apiType == om2.MFn.kMatrixAttribute:
        return om2.MFnMatrixData(plug.asMObject()).matrix()

    # NUMBERS
    elif apiType == om2.MFn.kNumericAttribute:
        pType = om2.MFnNumericAttribute(pAttribute).numericType()
        if pType == om2.MFnNumericData.kBoolean:
            return plug.asBool()
        elif pType in [
            om2.MFnNumericData.kShort,
            om2.MFnNumericData.kInt,
            om2.MFnNumericData.kLong,
            om2.MFnNumericData.kByte,
        ]:
            return plug.asInt()
        elif pType in [
            om2.MFnNumericData.kFloat,
            om2.MFnNumericData.kDouble,
            om2.MFnNumericData.kAddr,
        ]:
            return plug.asDouble()

    # Enum
    elif apiType == om2.MFn.kEnumAttribute:
        return plug.asInt()

    return None


def validateSourceNodes(nodes):
    """

    :param nodes: All the sourceNodes to process.
    :type nodes: `list`

    :return: `None`
    """

    print('nodes: {}'.format(nodes))
