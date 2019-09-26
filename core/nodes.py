from constants import serialization as c_serialization
from core import parser as c_parser


class ValidationNode:
    def __init__(self, name):
        """

        :param name: `str` name of the sourceNode holding the attribute we want to check
        """
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """
        :param name: `str`
        """
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._name = name

    def __repr__(self):
        return "%s" % self.name


class SourceNode(ValidationNode):
    def __init__(self, name, validityNodes=None):
        """
        Each ValidityNode will be considered a child of the sourceNode.
        This parent / child relationship holds everything we need to check a rig for validity.
        eg:
            myCtrlCrv has 2 attributes on it;
                - showCloth
                - headLock

            We can create a sourceNode of this ctrl curve.
            sourceNode = SourceNode(name="myCtrlCrv")

            Then can we create x# of ValidityNodes for EACH attribute we want to check is valid!
            eg:
            showCloth_geoHrc = ValidityNode(name="geo_hrc",
                                            attributeName="visibility", attributeValue=True,
                                            srcAttributeName="showCloth", srcAttributeValue="True"
                                            )
            sourceNode.addNodeToCheck(showCloth_geoHrc)

        It should also be noted we only serialize SourceNodes as ValidityNodes will be written as dependencies of these
        to disk as part of the SourceNode data.

        :param name: `str` unique name of the node as it exists in the dcc
        :param validityNodes: `list` of ValidityNodes
        """
        super(SourceNode, self).__init__(name=name)
        self._children = validityNodes or list()

    def addNodeToCheck(self, ValidityNode):
        """

        :param ValidityNode: `ValidityNode`
        """
        self._children.append(ValidityNode)

    def iterNodes(self):
        for eachNode in self._children:
            yield eachNode

    def toData(self):
        data = dict()
        data[c_serialization.KEY_NODENAME] = self._name
        data[c_serialization.KEY_VAILIDITYNODES] = list()
        for eachNode in self.iterNodes():
            data[c_serialization.KEY_VAILIDITYNODES].append(eachNode.toData())

        return data

    @classmethod
    def fromData(cls, data):
        """

        :param data: `dict`
        """
        nodeData = data.get(c_serialization.KEY_VAILIDITYNODES, list())
        validityNodes = list()
        for vd in nodeData:
            validityNode = ValidationNode(name=vd[c_serialization.KEY_NODENAME],
                                          attributeName=vd[c_serialization.KEY_ATTRIBUTENAME],
                                          attributeValue=vd[c_serialization.KEY_ATTRIBUTEVALUE],
                                          srcAttributeName=vd[c_serialization.KEY_SRC_ATTRIBUTENAME],
                                          srcAttributeValue=vd[c_serialization.KEY_SRC_ATTRIBUTEVALUE],
                                          )
            validityNodes.append(validityNode)

        inst = cls(name=data.get(c_serialization.KEY_NODENAME), validityNodes=validityNodes)

        return inst

    @classmethod
    def from_fileJSON(cls, filePath):
        data = c_parser.read(filepath=filePath)
        return cls.fromData(cls, data)

    def to_fileJSON(self, filePath):
        c_parser.write(filepath=filePath, data=self.toData())


class ValidityNode(ValidationNode):
    def __init__(self, name,
                 attributeName=None, attributeValue=None,
                 srcAttributeName=None, srcAttributeValue=None):
        """
        ValidityNodes hold some sourceNode data as these as children of the sourceNode and it makes sense to
        couple the data here rather than try to split across the SourceNode and the ValidityNode.

        Each ValidityNode is considered a validation check for a single ValidityNode.attribute (value) against a
        sourceNode.attribute (value).
        This way we can do the following checks:
        - Do these attributes even exist on the node??
        - Is the destination attribute connected to anything? If so is it the srcNode.attribute?
        - Does the srcNode.attribute = the expected srcNode.attributeValue? If not bail early! The rig is NOT in default
          state!
        - When the srcNode.attribute is correct, is the ValidityNode.attribute at the right value?

        :param name: `str` name of the node in the scene the ValidityNode.attribute exists on.
        :param attributeName: `str` name of the attribute on the node eg: showCloth
        :param attributeValue: `int`, `float`, `bool`, etc the expected value for this attribute when the
                                sourceAttribute's value match
        :param srcAttributeName: `str` name of the attribute on the sourceNode to match (note this node is a child of
                                the source node)
        :param srcAttributeValue: `int`, `float`, `bool`, etc the expected SOURCE value to be set for this value to be TRUE
        """
        super(ValidityNode, self).__init__(name=name)

        self._attributeName = attributeName
        self._attributeValue = attributeValue
        self._srcAttributeName = srcAttributeName
        self._srcAttributeValue = srcAttributeValue

    @property
    def attributeName(self):
        return self._attributeName

    @attributeName.setter
    def attributeName(self, name):
        """

        :param name: `str`
        :return:
        """
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._attributeName = name

    @property
    def attributeValue(self):
        return self._attributeValue

    @attributeValue.setter
    def attributeValue(self, value):
        """

        :param value:  `int`, `float, `bool`, etc
        """
        self._attributeValue = value

    @property
    def srcAttributeName(self):
        return self._srcAttributeName

    @srcAttributeName.setter
    def srcAttributeName(self, name):
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._srcAttributeName = name

    @property
    def srcAttributeValue(self):
        return self._srcAttributeValue

    @srcAttributeValue.setter
    def srcAttributeValue(self, value):
        """

        :param value: `int`, `float, `bool`, etc
        """
        self._srcAttributeValue = value

    def toData(self):
        data = dict()
        data[c_serialization.KEY_NODENAME] = self._name
        data[c_serialization.KEY_ATTRIBUTENAME] = self._attributeName
        data[c_serialization.KEY_ATTRIBUTEVALUE] = self._attributeValue
        data[c_serialization.KEY_SRC_ATTRIBUTENAME] = self._srcAttributeName
        data[c_serialization.KEY_SRC_ATTRIBUTEVALUE] = self._srcAttributeValue

        return data


class DefaultNode(ValidationNode):
    def __init__(self, name, defaultValue):
        super(DefaultNode, self).__init__(name=name)

        self._defaultValue = defaultValue

    @property
    def defaultValue(self):
        return self._defaultValue

    @defaultValue.setter
    def defaultValue(self, value):
        self._defaultValue = value

    def toData(self):
        data = dict()
        data[c_serialization.KEY_NODENAME] = self._name
        data[c_serialization.KEY_DEFAULTVALUE] = self._defaultValue

        return data
