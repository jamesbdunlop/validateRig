from const import constants as c_constants
from const import serialization as c_serialization
from core import parser as c_parser
import logging

logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self, name, longName, nodeType=c_serialization.NT_VALIDATIONNODE):
        """
        The base Node class inherited by everything else that should contain these fundamental methods/attrs etc

        :param name: `str` name of the Node
        """
        self._name = name.split("|")[-1].split(":")[-1]
        self._longName = longName
        self._nodeType = nodeType
        self._validationStatus = c_constants.NODE_VALIDATION_NA

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """
        :param name: `str`
        """
        self._name = name

    @property
    def longName(self):
        return self._longName

    @longName.setter
    def longName(self, longName):
        """
        :param name: `str`
        """
        self._longName = longName

    @property
    def nodeType(self):
        return self._nodeType

    @property
    def status(self):
        return self._validationStatus

    @status.setter
    def status(self, status):
        self._validationStatus = status

    def toData(self):
        self.data = dict()
        self.data[c_serialization.KEY_NODENAME] = self.name
        self.data[c_serialization.KEY_NODELONGNAME] = self.longName
        self.data[c_serialization.KEY_NODETYPE] = self.nodeType

        return self.data

    @classmethod
    def fromData(cls, data):
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        nodeType = data.get(c_serialization.KEY_NODETYPE, "")

        return cls(name=name, longName=longName, nodeType=nodeType)

    def __repr__(self):
        return "shortName: %s\nlongName: %s\nstatus: %s" % (
            self.name,
            self.longName,
            self.status,
        )


class SourceNode(Node):
    def __init__(self, name, longName, validityNodes=None):
        """
        Each ConnectionValidityNode will be considered a child of the sourceNode.
        This parent / child relationship holds everything we need to check a rig for validity.
        eg:
            myCtrlCrv has 2 attributes on it;
                - showCloth
                - headLock

            We can create a sourceNode of this ctrl curve.
            sourceNode = SourceNode(name="myCtrlCrv")

            Then can we create x# of ConnectionValidityNodes for EACH attribute we want to check is valid!
            eg:
            showCloth_geoHrc = ConnectionValidityNode(name="geo_hrc",
                                            attributeName="visibility", destAttrValue=True,
                                            srcAttrName="showCloth", srcAttrValue="True"
                                            )
            sourceNode.appendValidityNode(showCloth_geoHrc)

        It should also be noted we only serialize SourceNodes as ConnectionValidityNodes will be written as dependencies of these
        to disk as part of the SourceNode data.

        :param name: `str` unique name of the node as it exists in the dcc
        :param validityNodes: `list` of ConnectionValidityNodes
        """
        super(SourceNode, self).__init__(
            name=name, longName=longName, nodeType=c_serialization.NT_SOURCENODE
        )
        self._validityNodes = validityNodes or list()

    def validityNodeExists(self, validityNode):
        """

        :param validityNode: `str` short name
        :return: `bool`
        """
        for eachValidityNode in self.iterValidityNodes():
            if eachValidityNode.name == validityNode:
                return True

        return False

    def appendValidityNode(self, validityNode):
        """

        :param validityNode: `ValidityNode` DefaultValueNode or ConnectionValidityNode
        """
        if not self.validityNodeExists(validityNode.name):
            self._validityNodes.append(validityNode)
            return

    def appendValidityNodes(self, validityNodeList):
        for eachValidityNode in validityNodeList:
            self.appendValidityNode(eachValidityNode)

    def removeValidityNode(self, validityNode):
        """

        :param validityNode: `ValidityNode` DefaultValueNode or ConnectionValidityNode
        """
        for eachNode in self.iterValidityNodes():
            if eachNode == validityNode:
                self._validityNodes.remove(validityNode)

    def iterValidityNodes(self):
        for eachNode in self._validityNodes:
            yield eachNode

    @staticmethod
    def isNodeTypeEqualToDefaultValue(nodeType):
        """

        :param nodeType: `int`
        :return: `bool`
        """
        return nodeType == c_serialization.NT_DEFAULTVALUE

    @staticmethod
    def createValidityNodeFromData(data):
        """

        :param data: `dict`
        :return: `DefaultValueNode` | `ConnectionValidityNode`
        """

        nodeType = data[c_serialization.KEY_NODETYPE]
        if SourceNode.isNodeTypeEqualToDefaultValue(nodeType):
            return DefaultValueNode.fromData(data)

        return ConnectionValidityNode.fromData(data)

    def toData(self):
        super(SourceNode, self).toData()
        self.data[c_serialization.KEY_VAILIDITYNODES] = list()
        for eachNode in self.iterValidityNodes():
            self.data[c_serialization.KEY_VAILIDITYNODES].append(eachNode.toData())

        return self.data

    @classmethod
    def fromData(cls, data):
        """

        :param data: `dict` previously serialized SourceNode.toData()
        """
        sourceNodeName = data.get(c_serialization.KEY_NODENAME, None)
        sourceNodeLongName = data.get(c_serialization.KEY_NODELONGNAME, None)
        if sourceNodeName is None:
            raise KeyError("sourceNodeName is not valid! %s" % data)

        serializedValidityNodes = data.get(c_serialization.KEY_VAILIDITYNODES, list())
        validityNodes = [
            cls.createValidityNodeFromData(validityNodeData)
            for validityNodeData in serializedValidityNodes
        ]

        inst = cls(name=sourceNodeName, longName=sourceNodeLongName, validityNodes=validityNodes)

        return inst

    @classmethod
    def from_fileJSON(cls, filePath):
        """

        :param filePath: `str`
        :return:
        """
        data = c_parser.read(filepath=filePath)
        return cls.fromData(cls, data)

    def to_fileJSON(self, filePath):
        """

        :param filePath: `str`
        :return:
        """
        c_parser.write(filepath=filePath, data=self.toData())


class ConnectionValidityNode(Node):
    def __init__(self, name, longName):
        """
        ConnectionValidityNodes holds sourceNode.srcAttrName data as it makes sense to couple the data here rather than
        try to store data in the sourceData and pair it up with data in here.

        Each ConnectionValidityNode is considered a single validation check eg:
            `SourceNode.attribute` ----->  `ConnectionValidityNode.attribute`

        This way we can do something like the following boolean checks:
        SourceNode.attribute.exists()
        DestNode.attribute.exists()
        SourceNode.attribute.connectedTo(DestNode.attribute)
        SourceNode.attribute.value() == srcAttributeValue
        SourceNode.destAttribute.value() == destAttrValue

        :param name: `str` nodeName of the node that the sourceNode.attribute is connected to.
        :param nodeType: `int`
        """
        super(ConnectionValidityNode, self).__init__(
            name=name, longName=longName, nodeType=c_serialization.NT_CONNECTIONVALIDITY
        )
        # These should be set using the setters!
        self._destAttrName = ""
        self._destAttrValue = ""
        self._srcAttrName = ""
        self._srcAttrValue = ""
        self._status = False  # This is the report status if it passed or failed the validation test

    @property
    def destAttrName(self):
        """is name of the attribute on the node eg: showCloth"""
        return self._destAttrName

    @destAttrName.setter
    def destAttrName(self, name):
        """

        :param name: `str`
        :return:
        """
        self._destAttrName = name

    @property
    def destAttrValue(self):
        """`int`, `float`, `bool`, etc the expected value for this attribute when the sourceAttribute's value match"""
        return self._destAttrValue

    @destAttrValue.setter
    def destAttrValue(self, value):
        """

        :param value:  `int`, `float, `bool`, etc
        """
        self._destAttrValue = value

    @property
    def srcAttrName(self):
        """`str` name of the attribute on the sourceNode to match (note this node is a child of the sourceNode"""
        return self._srcAttrName

    @srcAttrName.setter
    def srcAttrName(self, name):
        self._srcAttrName = name

    @property
    def srcAttrValue(self):
        """`int`, `float`, `bool`, etc This is the expected SourceNode.attribute value."""
        return self._srcAttrValue

    @srcAttrValue.setter
    def srcAttrValue(self, value):
        """

        :param value: `int`, `float, `bool`, etc
        """
        self._srcAttrValue = value

    def toData(self):
        super(ConnectionValidityNode, self).toData()
        self.data[c_serialization.KEY_SRC_ATTRIBUTENAME] = self._srcAttrName
        self.data[c_serialization.KEY_SRC_ATTRIBUTEVALUE] = self._srcAttrValue
        self.data[c_serialization.KEY_DEST_ATTRIBUTENAME] = self._destAttrName
        self.data[c_serialization.KEY_DEST_ATTRIBUTEVALUE] = self._destAttrValue

        return self.data

    @classmethod
    def fromData(cls, data):
        name = data.get(c_serialization.KEY_NODENAME, "")
        longname = data.get(c_serialization.KEY_NODELONGNAME, "")

        inst = cls(name=name, longName=longname)
        inst.srcAttrName = data.get(c_serialization.KEY_SRC_ATTRIBUTENAME, "na")
        inst.srcAttrValue = data.get(c_serialization.KEY_SRC_ATTRIBUTEVALUE, 0)
        inst.destAttrName = data.get(c_serialization.KEY_DEST_ATTRIBUTENAME, "na")
        inst.destAttrValue = data.get(c_serialization.KEY_DEST_ATTRIBUTEVALUE, 0)

        return inst


class DefaultValueNode(Node):
    def __init__(self, name, longName="", defaultValue=None):
        super(DefaultValueNode, self).__init__(name=name, longName=longName, nodeType=c_serialization.NT_DEFAULTVALUE)
        self._defaultValue = defaultValue

    @property
    def defaultValue(self):
        return self._defaultValue

    @defaultValue.setter
    def defaultValue(self, value):
        self._defaultValue = value

    def toData(self):
        super(DefaultValueNode, self).toData()
        self.data[c_serialization.KEY_DEFAULTVALUE] = self._defaultValue

        return self.data

    @classmethod
    def fromData(cls, data):
        name = data.get(c_serialization.KEY_NODENAME, "")
        longname = data.get(c_serialization.KEY_NODELONGNAME, "")
        value = data.get(c_serialization.KEY_DEFAULTVALUE, "")

        return cls(name=name, longName=longname, defaultValue=value)
