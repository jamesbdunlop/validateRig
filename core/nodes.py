#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtCore
from core import parser as c_parser
from const import constants as vrc_constants
from const import serialization as c_serialization

logger = logging.getLogger(__name__)


class Node(QtCore.QObject):
    def __init__(
        self, name, longName, nodeType=c_serialization.NT_VALIDATIONNODE, parent=None,
    ):
        # type: (str, str, int, Node) -> None
        self._name = name
        self._longName = longName
        self._nodeType = nodeType
        self._validationStatus = vrc_constants.NODE_VALIDATION_NA
        self._parent = parent
        self._children = list()
        self._nameSpace = self._longName.split("|")[-1].split(":")[0]
        self._showNameSpace = False
        self._displayName = self._name
        self._nameSpace = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        self._name = name

    @property
    def nameSpace(self):
        return self._nameSpace

    @nameSpace.setter
    def nameSpace(self, nameSpace):
        # type: (str) -> None
        self._nameSpace = nameSpace
        self.updateNameSpaceInLongName()

    @property
    def displayName(self):
        return self._displayName

    @displayName.setter
    def displayName(self, name):
        # type: (str) -> None
        self._displayName = name

    @property
    def longName(self):
        return self._longName

    @longName.setter
    def longName(self, longName):
        # type: (str) -> None
        self._longName = longName

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        # type: (SourceNode) -> None
        self._parent = parent

    @property
    def nodeType(self):
        return self._nodeType

    @property
    def status(self):
        return self._validationStatus

    @status.setter
    def status(self, status):
        # type: (str) -> None
        self._validationStatus = status

    def createNameSpacedShortName(self):
        # type: () -> str
        ns = "{}:{}".format(self.nameSpace, self.name)
        return ns

    def updateNameSpaceInLongName(self):
        # type: (str) -> None
        longName = self.longName
        if "|" in longName:
            splitPipe = longName.split("|")[1:]
            splitNS = ["{}:{}".format(self.nameSpace, n.split(":")[-1]) for n in splitPipe]
            newLongName = "|{}".format("|".join(splitNS))
        else:
            newLongName = self.createNameSpacedShortName()

        self.longName = newLongName

    def setNameSpaceInDisplayName(self):
        # type: (bool) -> None
        self.displayName = self.createNameSpacedShortName()

    def setLongNameInDisplayName(self):
        # type: (bool) -> None
        self.displayName = self.longName

    def addChild(self, node):
        # type: (Node) -> None
        if node not in self._children:
            self._children.append(node)
            node.parent = self

    def addChildren(self, nodes):
        # type: (list[Node]) -> None
        for node in nodes:
            self.addChild(node)

    def removeChild(self, node):
        # type: (Node) -> None
        for eachNode in self._children:
            if eachNode == node:
                node.parent = None
                self._children.remove(node)

    def iterChildren(self):
        # type: () -> Generator[Node]
        for eachNode in self._children:
            yield eachNode

    def iterDescendants(self):
        for eachNode in self._children:
            yield eachNode
            for eachChild in eachNode._children:
                yield eachChild

    def toData(self):
        self.data = dict()
        self.data[c_serialization.KEY_NODENAME] = self.name
        self.data[c_serialization.KEY_NODELONGNAME] = self.longName
        self.data[c_serialization.KEY_NODEDISPLAYNAME] = self.displayName
        self.data[c_serialization.KEY_NODENAMESPACE] = self.nameSpace
        self.data[c_serialization.KEY_NODETYPE] = self.nodeType

        return self.data

    @classmethod
    def fromData(cls, data):
        # type: (dict) -> Node
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        nameSpace = data.get(c_serialization.KEY_NODENAMESPACE, "")
        nodeType = data.get(c_serialization.KEY_NODETYPE, "")

        inst = cls(name=name, longName=longName, nodeType=nodeType)
        inst.displayName = displayName
        inst.nameSpace = nameSpace

        return inst

    def __repr__(self):
        return "shortName: %s\nlongName: %s\ndisplayName: %s\nnodeType: %s\nstatus: %s" % (
            self.name,
            self.longName,
            self.displayName,
            self.nodeType,
            self.status,
        )


class SourceNode(Node):
    def __init__(self, name, longName, validityNodes=None, parent=None, **kwargs):
        # type: (str, str, list, Node) -> None
        """
        Args:
            name: a unique name of the node as it exists in the dcc
            validityNodes: list of nodes [ValidityNode,ValidityNode]
        """
        super(SourceNode, self).__init__(
            name=name, longName=longName, nodeType=c_serialization.NT_SOURCENODE, parent=parent,
        )
        self._children = validityNodes or list()

    @staticmethod
    def isNodeTypeEqualToDefaultValue(nodeType):
        # type: (int) -> bool
        return nodeType == c_serialization.NT_DEFAULTVALUE

    @staticmethod
    def createValidityNodeFromData(data, parent=None):
        # type: (dict) -> Node
        nodeType = data[c_serialization.KEY_NODETYPE]
        if SourceNode.isNodeTypeEqualToDefaultValue(nodeType):
            return DefaultValueNode.fromData(data, parent)

        return ConnectionValidityNode.fromData(data, parent)

    def toData(self):
        super(SourceNode, self).toData()
        self.data[c_serialization.KEY_VAILIDITYNODES] = list()
        for eachNode in self.iterChildren():
            self.data[c_serialization.KEY_VAILIDITYNODES].append(eachNode.toData())

        return self.data

    @classmethod
    def fromData(cls, data):
        # type: (dict) -> SourceNode
        """
        Args:
            data: previously serialized SourceNode.toData() ususally loaded from .json
        """
        sourceNodeName = data.get(c_serialization.KEY_NODENAME, None)
        sourceNodeLongName = data.get(c_serialization.KEY_NODELONGNAME, None)
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        nameSpace = data.get(c_serialization.KEY_NODENAMESPACE, "")
        if sourceNodeName is None:
            raise KeyError("NoneType is not a valid sourceNodeName!")

        inst = cls(name=sourceNodeName, longName=sourceNodeLongName)

        serializedValidityNodes = data.get(c_serialization.KEY_VAILIDITYNODES, list())
        validityNodes = [
            cls.createValidityNodeFromData(validityNodeData, inst)
            for validityNodeData in serializedValidityNodes
        ]
        inst.addChildren(validityNodes)
        inst.displayName = displayName
        inst.nameSpace = nameSpace
        return inst


class ConnectionValidityNode(Node):
    def __init__(self, name, longName, parent=None):
        # type: (str, str, Node) -> None
        """
        ConnectionValidityNode holds sourceNode.srcAttrName data as it makes sense to me to couple the data here
        rather than try to store data in the sourceData and pair it up with data in here.

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
            name=name,
            longName=longName,
            parent=parent,
            nodeType=c_serialization.NT_CONNECTIONVALIDITY,
        )

        self._destAttrName = ""
        self._destAttrValue = ""
        self._srcAttrName = ""
        self._srcAttrValue = ""

    @property
    def destAttrName(self):
        """is name of the attribute on the node eg: showCloth"""
        return self._destAttrName

    @destAttrName.setter
    def destAttrName(self, name):
        # type: (str) -> None
        self._destAttrName = name

    @property
    def destAttrValue(self):
        """`int`, `float`, `bool`, etc the expected value for this attribute when the sourceAttribute's value match"""
        return self._destAttrValue

    @destAttrValue.setter
    def destAttrValue(self, value):
        # type: (any) -> None
        """
        Args:
            value:  `int`, `float, `bool`, etc
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
    def fromData(cls, data, parent):
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        nameSpace = data.get(c_serialization.KEY_NODENAMESPACE, "")

        inst = cls(name=name, longName=longName)
        inst.srcAttrName = data.get(c_serialization.KEY_SRC_ATTRIBUTENAME, "na")
        inst.srcAttrValue = data.get(c_serialization.KEY_SRC_ATTRIBUTEVALUE, 0)
        inst.destAttrName = data.get(c_serialization.KEY_DEST_ATTRIBUTENAME, "na")
        inst.destAttrValue = data.get(c_serialization.KEY_DEST_ATTRIBUTEVALUE, 0)

        inst.displayName = displayName
        inst.nameSpace = nameSpace

        return inst


class DefaultValueNode(Node):
    def __init__(self, name, longName, defaultValue=None, parent=None):
        # type: (str, str, any, Node) -> None
        super(DefaultValueNode, self).__init__(
            name=name,
            longName=longName,
            parent=parent,
            nodeType=c_serialization.NT_DEFAULTVALUE,
        )
        self._defaultValue = defaultValue

    @property
    def defaultValue(self):
        return self._defaultValue

    @defaultValue.setter
    def defaultValue(self, value):
        # type: (any) -> None
        self._defaultValue = value

    def toData(self):
        super(DefaultValueNode, self).toData()
        self.data[c_serialization.KEY_DEFAULTVALUE] = self._defaultValue

        return self.data

    @classmethod
    def fromData(cls, data, parent):
        # type: (dict, Node) -> DefaultValueNode
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        value = data.get(c_serialization.KEY_DEFAULTVALUE, "")
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        nameSpace = data.get(c_serialization.KEY_NODENAMESPACE, "")

        inst = cls(name=name, longName=longName, defaultValue=value, parent=parent)
        inst.displayName = displayName
        inst.nameSpace = nameSpace

        return inst
