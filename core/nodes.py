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
        self._displayName = self._name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        self._name = name

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
        self.data[c_serialization.KEY_NODETYPE] = self.nodeType

        return self.data

    @classmethod
    def fromData(cls, data):
        # type: (dict) -> Node
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        nodeType = data.get(c_serialization.KEY_NODETYPE, "")

        inst = cls(name=name, longName=longName, nodeType=nodeType)
        inst.displayName = displayName

        return inst

    def __repr__(self):
        return (
            "shortName: %s\nlongName: %s\ndisplayName: %s\nnodeType: %s\nstatus: %s"
            % (self.name, self.longName, self.displayName, self.nodeType, self.status,)
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
            name=name,
            longName=longName,
            nodeType=c_serialization.NT_SOURCENODE,
            parent=parent,
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
        return inst


class ConnectionValidityNode(Node):
    def __init__(self, name, longName, parent=None):
        # type: (str, str, Node) -> None
        super(ConnectionValidityNode, self).__init__(
            name=name,
            longName=longName,
            parent=parent,
            nodeType=c_serialization.NT_CONNECTIONVALIDITY,
        )

        self._connectionData = dict()

    @property
    def connectionData(self):
        return self._connectionData

    @connectionData.setter
    def connectionData(self, data):
        self._connectionData = data

    def toData(self):
        super(ConnectionValidityNode, self).toData()
        self.data[c_serialization.KEY_CONNDATA] = self._connectionData
        return self.data

    @classmethod
    def fromData(cls, data, parent):
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        connectionData = data.get(c_serialization.KEY_CONNDATA, dict())

        inst = cls(name=name, longName=longName)
        inst.displayName = displayName
        inst.connectionData = connectionData

        return inst


class DefaultValueNode(Node):
    def __init__(self, name, longName, parent=None):
        # type: (str, str, any, Node) -> None
        super(DefaultValueNode, self).__init__(
            name=name,
            longName=longName,
            parent=parent,
            nodeType=c_serialization.NT_DEFAULTVALUE,
        )
        self._defaultValueData = dict()

    @property
    def defaultValueData(self):
        return self._defaultValueData

    @defaultValueData.setter
    def defaultValueData(self, data):
        self._defaultValueData = data

    def toData(self):
        super(DefaultValueNode, self).toData()
        self.data[c_serialization.KEY_DEFAULTVALUEDATA] = self._defaultValueData

        return self.data

    @classmethod
    def fromData(cls, data, parent):
        # type: (dict, Node) -> DefaultValueNode
        name = data.get(c_serialization.KEY_NODENAME, "")
        longName = data.get(c_serialization.KEY_NODELONGNAME, "")
        displayName = data.get(c_serialization.KEY_NODEDISPLAYNAME, "")
        defaultValueData = data.get(c_serialization.KEY_DEFAULTVALUEDATA, dict())

        inst = cls(name=name, longName=longName, parent=parent)
        inst.displayName = displayName
        inst.defaultValueData = defaultValueData

        return inst
