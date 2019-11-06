import logging
from const import serialization as c_serialization
from core.nodes import SourceNode
from core import parser as c_parser
from core import inside

logger = logging.getLogger(__name__)

if inside.insideMaya():
    import maya.api.OpenMaya as om2
    from maya import cmds


class Validator:
    def __init__(self, name, namespace="", nodes=None):
        self._name = name  # name of the validator.
        self._namespace = namespace
        self._nodes = (
            nodes or list()
        )  # list of SourceNodes with ConnectionValidityNodes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """

        :param name:`str` name of the validator
        :return:
        """
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._name = name

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    def findSourceNodeByLongName(self, name):
        """

        :param name: `str`
        :return: `SourceNode`
        """
        for eachNode in self.iterSourceNodes():
            if eachNode.longName == name:
                return eachNode

    def sourceNodeExists(self, sourceNode):
        """

        :param sourceNode: `SourceNode`
        :return:
        """
        sourceNodeNames = [sn.longName for sn in self._nodes]

        return sourceNode.longName in sourceNodeNames

    def sourceNodeNameExists(self, sourceNodeLongName):
        """

        :param sourceNodeLongName: `str`
        :return:
        """
        sourceNodeNames = [n.longName for n in self._nodes]
        logger.debug("{} sourceNodeNames: {}".format(sourceNodeLongName, sourceNodeNames))
        return sourceNodeLongName in sourceNodeNames

    def replaceExistingSourceNode(self, sourceNode):
        """
        Replace an existing index in the list with the sourceNode
        :param sourceNode: `SourceNode`
        :return: `bool`
        """
        for x, node in enumerate(self._nodes):
            if node.longName == sourceNode.longName:
                self._nodes[x] = sourceNode
                return sourceNode

    def addSourceNode(self, sourceNode, force=False):
        """
        :param sourceNode: `SourceNode`
        :param force: `bool`
        """

        if not self.sourceNodeExists(sourceNode):
            self._nodes.append(sourceNode)
            return sourceNode

        if self.sourceNodeExists(sourceNode) is not None and force:
            return self.replaceExistingSourceNode(sourceNode)

        if self.sourceNodeExists(sourceNode) and not force:
            raise IndexError(
                "%s already exists in validator. Use force=True if you want to overwrite existing!"
                % sourceNode
            )

    def addSourceNodeFromData(self, data):
        """

        :param data: `dict`
        :return: `SourceNode`
        """
        sourceNode = SourceNode.fromData(data)
        self.addSourceNode(sourceNode)

        return sourceNode

    def removeSourceNode(self, sourceNode):
        for eachSourceNode in self.iterSourceNodes():
            if eachSourceNode == sourceNode:
                self._nodes.remove(eachSourceNode)
                return True

        return False

    def iterSourceNodes(self):
        for eachNode in self._nodes:
            yield eachNode

    def validateSourceNodes(self):
        raise NotImplementedError("Override this..")

    def remedyFailedValidations(self):
        raise NotImplementedError("Override this..")

    def toData(self):
        data = dict()
        data[c_serialization.KEY_VALIDATOR_NAME] = self.name
        data[c_serialization.KEY_VALIDATOR_NODES] = list()
        for eachNode in self.iterSourceNodes():
            data[c_serialization.KEY_VALIDATOR_NODES].append(eachNode.toData())

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
        logger.info("Writing validator to: %s" % filePath)
        c_parser.write(filepath=filePath, data=self.toData())
        logger.info("Successfully wrote validator to: %s" % filePath)
        return True

    def __repr__(self):
        return "%s" % self.name


class MayaValidator(Validator):
    def __init__(self, name):
        super(MayaValidator, self).__init__(name=name)

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

    def validateAllSourceNodes(self):
        """
        Maya validator checking for values against the expected values!
        """
        validationData = dict()
        for validityNode in self.iterSourceNodes():
            nodeType = validityNode.nodeType()

            mSel = om2.MSelectionList()
            mSel.add("{}:{}".format(self.namespace, validityNode.name))
            srcMFn = om2.MFnDependencyNode(mSel.getDependNode(0))

    def remedyFailedValidations(self):
        def fixConnections():
            pass

        def fixDefaultValues():
            pass

        pass
