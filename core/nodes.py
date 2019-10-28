from const import serialization as c_serialization
from core import parser as c_parser
import logging
logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self, name, nodeType=c_serialization.NT_VALIDATIONNODE):
        """
        The base Node class inherited by everything else that should contain these fundamental methods/attrs etc

        :param name: `str` name of the Node
        """
        self._name = name
        self._nodeType = nodeType

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

    @property
    def nodeType(self):
        return self._nodeType

    def toData(self):
        self.data = dict()
        self.data[c_serialization.KEY_NODENAME] = self.name
        self.data[c_serialization.KEY_NODTYPE] = self.nodeType

        return self.data

    @classmethod
    def fromData(cls, data):
        name = data.get(c_serialization.KEY_NODENAME, "")
        nodeType = data.get(c_serialization.KEY_NODTYPE, "")

        return cls(name=name, nodeType=nodeType)

    def __repr__(self):
        return "%s" % self.name


class SourceNode(Node):
    def __init__(self, name, nodeType=c_serialization.NT_SOURCENODE, validityNodes=None):
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
            sourceNode.addValidityNode(showCloth_geoHrc)

        It should also be noted we only serialize SourceNodes as ConnectionValidityNodes will be written as dependencies of these
        to disk as part of the SourceNode data.

        :param name: `str` unique name of the node as it exists in the dcc
        :param validityNodes: `list` of ConnectionValidityNodes
        """
        super(SourceNode, self).__init__(name=name, nodeType=nodeType)
        self._validity = validityNodes or list()

    def validityNodeExists(self, connectionValidityNodeName):
        for eachValidityNode in self.iterValidityNodes():
            if eachValidityNode.name == connectionValidityNodeName:
                return True

        return False

    def addValidityNode(self, validityNode):
        """

        :param validityNode: `ValidityNode` Default or Connection
        """
        if not self.validityNodeExists(validityNode.name):
            self._validity.append(validityNode)
        else:
            logger.warning("ValidityNode already exists, skipping")

    def iterValidityNodes(self):
        for eachNode in self._validity:
            yield eachNode

    def toData(self):
        super(SourceNode, self).toData()
        self.data[c_serialization.KEY_VAILIDITYNODES] = list()
        for eachNode in self.iterValidityNodes():
            self.data[c_serialization.KEY_VAILIDITYNODES].append(eachNode.toData())

        return self.data

    @classmethod
    def fromData(cls, data):
        """

        :param data: `dict`
        """
        nodeData = data.get(c_serialization.KEY_VAILIDITYNODES, list())
        validityNodes = list()
        for vd in nodeData:
            validityNode = None
            if vd[c_serialization.KEY_NODTYPE] == c_serialization.NT_CONNECTIONVALIDITY:
                validityNode = ConnectionValidityNode.fromData(vd)

            elif vd[c_serialization.KEY_NODTYPE] == c_serialization.NT_DEFAULTVALUE:
                validityNode = DefaultValueNode.fromData(vd)

            if validityNode is None:
                continue

            validityNodes.append(validityNode)

        inst = cls(name=data.get(c_serialization.KEY_NODENAME), validityNodes=validityNodes)

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
    def __init__(self, name, nodeType=c_serialization.NT_CONNECTIONVALIDITY,
                 destAttrName=None, destAttrValue=None,
                 srcAttrName=None, srcAttrValue=None):
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
        :param destAttrName: `str` name of the attribute on the node eg: showCloth
        :param destAttrValue: `int`, `float`, `bool`, etc the expected value for this attribute when the
                              sourceAttribute's value match
        :param srcAttrName: `str` name of the attribute on the sourceNode to match (note this node is a child of
                             the source node)
        :param srcAttrValue: `int`, `float`, `bool`, etc This is the expected SourceNode.attribute value.
        """
        super(ConnectionValidityNode, self).__init__(name=name, nodeType=nodeType)

        self._destAttrName = destAttrName
        self._destAttrValue = destAttrValue
        self._srcAttrName = srcAttrName
        self._srcAttrValue = srcAttrValue
        self._status = False    # This is the report status if it passed or failed the validation test

    @property
    def destAttrName(self):
        return self._destAttrName

    @destAttrName.setter
    def destAttrName(self, name):
        """

        :param name: `str`
        :return:
        """
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._destAttrName = name

    @property
    def destAttrValue(self):
        return self._destAttrValue

    @destAttrValue.setter
    def destAttrValue(self, value):
        """

        :param value:  `int`, `float, `bool`, etc
        """
        self._destAttrValue = value

    @property
    def srcAttrName(self):
        return self._srcAttrName

    @srcAttrName.setter
    def srcAttrName(self, name):
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._srcAttrName = name

    @property
    def srcAttrValue(self):
        return self._srcAttrValue

    @srcAttrValue.setter
    def srcAttrValue(self, value):
        """

        :param value: `int`, `float, `bool`, etc
        """
        self._srcAttrValue = value

    def toData(self):
        super(ConnectionValidityNode, self).toData()
        self.data[c_serialization.KEY_DEST_ATTRIBUTENAME] = self._destAttrName
        self.data[c_serialization.KEY_DEST_ATTRIBUTEVALUE] = self._destAttrValue
        self.data[c_serialization.KEY_SRC_ATTRIBUTENAME] = self._srcAttrName
        self.data[c_serialization.KEY_SRC_ATTRIBUTEVALUE] = self._srcAttrValue

        return self.data

    @classmethod
    def fromData(cls, data):
        name = data.get(c_serialization.KEY_NODENAME, "")
        nodetype = data.get(c_serialization.KEY_NODTYPE, "")

        destAttrName = data.get(c_serialization.KEY_DEST_ATTRIBUTENAME, "")
        destAttrValue = data.get(c_serialization.KEY_DEST_ATTRIBUTEVALUE, "")
        srcAttrName = data.get(c_serialization.KEY_SRC_ATTRIBUTENAME, "")
        srcAttrValue = data.get(c_serialization.KEY_SRC_ATTRIBUTEVALUE, "")

        return cls(name=name, nodeType=nodetype,
                   destAttrName=destAttrName, destAttrValue=destAttrValue,
                   srcAttrName=srcAttrName, srcAttrValue=srcAttrValue)


class DefaultValueNode(Node):
    def __init__(self, name, nodeType=c_serialization.NT_DEFAULTVALUE, defaultValue=None):
        super(DefaultValueNode, self).__init__(name=name, nodeType=nodeType)

        self._defaultValue = defaultValue

    @property
    def defaultValue(self):
        return self._defaultValue

    @defaultValue.setter
    def defaultValue(self, value):
        self._defaultValue = value

    def toData(self):
        super(DefaultValueNode, self).toData()
        self.data[c_serialization.KEY_NODENAME] = self._name
        self.data[c_serialization.KEY_NODTYPE] = self.nodeType
        self.data[c_serialization.KEY_DEFAULTVALUE] = self._defaultValue

        return self.data

    @classmethod
    def fromData(cls, data):
        name = data.get(c_serialization.KEY_NODENAME, "")
        nodetype = data.get(c_serialization.KEY_NODTYPE, "")
        value = data.get(c_serialization.KEY_DEFAULTVALUE, "")

        return cls(name=name, nodeType=nodetype, defaultValue=value)
