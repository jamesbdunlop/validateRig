import logging
from constants import serialization as c_serialization
from core import parser as c_parser

logger = logging.getLogger(__name__)


class Validator:
    def __init__(self, name, nodes=None):
        self._name = name                   # name of the validator.
        self._nodes = nodes or list()       # list of SourceNodes with ValidityNodes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._name = name

    def sourceNodeExists(self, sourceNode):
        sourceNodeNames = [n.name for n in self._nodes]

        return sourceNode.name in sourceNodeNames

    def _addExistingNode(self, sourceNode):
        """
        Replace an existing index in the list with the sourceNode
        :param sourceNode: `SourceNode`
        :return: `bool`
        """
        for x, node in enumerate(self._nodes):
            if node.name == sourceNode.name:
                self._nodes[x] = sourceNode
                return True
        return False

    def addNodeToValidate(self, sourceNode, force=False):
        """
        :param sourceNode: `SourceNode`
        :param force: `bool`
        """

        if not self.sourceNodeExists(sourceNode):
            self._nodes.append(sourceNode)
            return True

        if self.sourceNodeExists(sourceNode) and force:
            return self._addExistingNode(sourceNode)

        if self.sourceNodeExists(sourceNode) and not force:
            raise IndexError("%s already exists in validator. Use force=True if you want to overwrite existing!" % sourceNode)

    def iterNodes(self):
        for eachNode in self._nodes:
            yield eachNode

    def sourceNodeByName(self, name):
        for eachNode in self.iterNodes():
            if eachNode.name == name:
                return eachNode

    def validate(self):
        raise NotImplementedError('Override this..')

    def toData(self):
        data = dict()
        data[c_serialization.KEY_VALIDATOR_NAME] = self.name
        data[c_serialization.KEY_VALIDATOR_SOURCENODES] = list()
        for eachSourceNode in self.iterNodes():
            data[c_serialization.KEY_VALIDATOR_SOURCENODES].append(eachSourceNode.toData())

        return data

    @classmethod
    def fromData(cls, data):
        """

        :param data: `dict`
        """
        pass

    @classmethod
    def from_fileJSON(cls, filePath):
        data = c_parser.read(filepath=filePath)
        return cls.fromData(cls, data)

    def to_fileJSON(self, filePath):
        c_parser.write(filepath=filePath, data=self.toData())

        return True


class MayaValidator(Validator):
    def __init__(self, name):
        super(MayaValidator, self).__init__(name=name)

    def getPlugValue(self, plug):
        """
        :param plug: MPlug
        :return: The value of the passed in MPlug or None
        """
        import maya.api.OpenMaya as om2

        pAttribute = plug.attribute()
        apiType = pAttribute.apiType()

        # Float Groups - rotate, translate, scale; Com2pounds
        if apiType in [om2.MFn.kAttribute3Double, om2.MFn.kAttribute3Float, om2.MFn.kCompoundAttribute]:
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
            elif pType in [om2.MFnNumericData.kShort, om2.MFnNumericData.kInt, om2.MFnNumericData.kLong,
                           om2.MFnNumericData.kByte]:
                return plug.asInt()
            elif pType in [om2.MFnNumericData.kFloat, om2.MFnNumericData.kDouble, om2.MFnNumericData.kAddr]:
                return plug.asDouble()

        # Enum
        elif apiType == om2.MFn.kEnumAttribute:
            return plug.asInt()

        return None

    def validate(self):
        """
        Maya validator checking for values against the expected values!
        """
        import maya.api.OpenMaya as om2

        validationData = dict()
        for srcNode in self.iterNodes():
            mSel = om2.MSelectionList()
            mSel.add(srcNode.name)
            srcMFn = om2.MFnDependencyNode(mSel.getDependNode(0))

            for destNode in srcNode.iterNodes():
                srcPlug = srcMFn.findPlug(destNode.srcAttributeName, False)
                expectedSourceValue = destNode.srcAttributeValue

                # We can bail out early if the source attribute in scene doesn't match the expected validation setting!
                srcPlugValue = self.getPlugValue(srcPlug)
                if srcPlugValue != expectedSourceValue:
                    validationData[srcNode.name] = "Failed %s.%s is not set at %s" % (srcNode.name,
                                                                                      destNode.srcAttributeName,
                                                                                      expectedSourceValue)
