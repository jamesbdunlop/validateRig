import unittest
import logging
from vrConst import serialization as c_serialization
from vrConst import testData as c_testData
import core.nodes as c_nodes

logger = logging.getLogger(__name__)
# TODO set status tests and anything else missing from base node


class Test_Nodes(unittest.TestCase):
    def setUp(self):
        # Names locally etc
        self.sourceNodeName = c_testData.SRC_NODENAME
        self.srcNodeAttrName = c_testData.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testData.SRC_ATTRVALUE
        self.sourceNodeType = c_testData.SRC_NODETYPE

        self.connectionValidityNodeName = c_testData.VALIDITY_NODENAME
        self.connectionValidityNodeAttrName = c_testData.VALIDITY_DEST_ATTRNAME
        self.connectionValidityNodeAttrValue = c_testData.VALIDITY_DEST_ATTRVALUE
        self.connectionValidityNodeType = c_testData.VALIDITY_NODETYPE

        self.defaultValueNodeName = c_testData.DEFAULT_NODENAME
        self.defaultValueNodeValue = c_testData.DEFAULT_NODEVALUE
        self.defaultValueNodeType = c_testData.DEFAULT_NODETYPE

        # Nodes now
        self.sourceNode = c_nodes.SourceNode(
            name=self.sourceNodeName, longName=self.sourceNodeName
        )

        self.connectionValidityNode = c_nodes.ConnectionValidityNode(
            name=self.connectionValidityNodeName,
            longName=self.connectionValidityNodeName,
        )
        self.connectionValidityNode.destAttrName = self.connectionValidityNodeAttrName
        self.connectionValidityNode.destAttrValue = self.connectionValidityNodeAttrValue
        self.connectionValidityNode.srcAttrName = self.srcNodeAttrName
        self.connectionValidityNode.srcAttrValue = self.srcNodeAttrValue

        self.defaultValueNode = c_nodes.DefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
            defaultValue=self.defaultValueNodeValue
        )

        self.sourceNode.addChild(self.connectionValidityNode)
        self.sourceNode.addChild(self.defaultValueNode)

        self.expectedToData = {
            c_serialization.KEY_NODENAME: self.sourceNodeName,
            c_serialization.KEY_NODELONGNAME: self.sourceNodeName,
            c_serialization.KEY_NODETYPE: self.sourceNodeType,
            c_serialization.KEY_VAILIDITYNODES: [
                {
                    c_serialization.KEY_NODENAME: self.connectionValidityNodeName,
                    c_serialization.KEY_NODELONGNAME: self.connectionValidityNodeName,
                    c_serialization.KEY_NODETYPE: self.connectionValidityNodeType,
                    c_serialization.KEY_DEST_ATTRIBUTENAME: self.connectionValidityNodeAttrName,
                    c_serialization.KEY_DEST_ATTRIBUTEVALUE: self.connectionValidityNodeAttrValue,
                    c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                    c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue,
                },
                {
                    c_serialization.KEY_NODENAME    : self.defaultValueNodeName,
                    c_serialization.KEY_NODELONGNAME: self.defaultValueNodeName,
                    c_serialization.KEY_NODETYPE    : self.defaultValueNodeType,
                    c_serialization.KEY_DEFAULTVALUE: self.defaultValueNodeValue,
                    }
            ],
        }

    def test_instanceTypes(self):
        self.assertIsInstance(self.sourceNode, c_nodes.Node)
        self.assertIsInstance(self.defaultValueNode, c_nodes.DefaultValueNode)
        self.assertIsInstance(self.connectionValidityNode, c_nodes.ConnectionValidityNode)

    def test_sourceNodeName(self):
        self.assertEqual(
            self.sourceNodeName,
            self.sourceNode.name,
            "srcNodeName is not %s" % self.sourceNodeName,
        )

    def test_srcNode_iterChildren(self):
        nodes = [n for n in self.sourceNode.iterChildren()]

        self.assertEqual(len(nodes), 2, "Length of itrNodes is not 1!")
        self.assertEqual(
            nodes[0],
            self.connectionValidityNode,
            "[0] Node is not %s" % self.connectionValidityNode,
        )
        self.assertEqual(
            nodes[1],
            self.defaultValueNode,
            "[0] Node is not %s" % self.defaultValueNode,
        )

    def test_sourceNode_toData(self):
        self.assertEqual(
            self.sourceNode.toData(),
            self.expectedToData,
            "%s doesn't match! %s" % (self.sourceNode.toData(), self.expectedToData),
        )

    def test_connectionValidityNode_name(self):
        self.assertEqual(
            self.connectionValidityNodeName,
            self.connectionValidityNode.name,
            "connectionValidityNodeName is not %s" % self.connectionValidityNodeName,
        )

    def test_connectionValidityNode_destAttrName(self):
        self.assertEqual(
            self.connectionValidityNodeAttrName,
            self.connectionValidityNode.destAttrName,
            "connectionValidityNode.destAttrName is not %s"
            % self.connectionValidityNodeAttrName,
        )

    def test_connectionValidityNode_destAttrValuee(self):
        self.assertEqual(
            self.connectionValidityNodeAttrValue,
            self.connectionValidityNode.destAttrValue,
            "connectionValidityNode.destAttrValue is not %s"
            % self.connectionValidityNodeAttrValue,
        )

    def test_connectionValidityNode_srcAttrName(self):
        self.assertEqual(
            self.srcNodeAttrName,
            self.connectionValidityNode._srcAttrName,
            "srcAttrName is not %s" % self.srcNodeAttrName,
        )

    def test_connectionValidityNode_srcAttrValue(self):
        self.assertEqual(
            self.srcNodeAttrValue,
            self.connectionValidityNode.srcAttrValue,
            "srcAttrValue is not %s" % self.srcNodeAttrValue,
        )

    def test_defaultValueNode_name(self):
        self.assertEqual(
            self.defaultValueNodeName,
            self.defaultValueNode.name,
            "defaultValueNode.name is not %s" % self.defaultValueNodeName,
            )

    def test_defaultValueNode_value(self):
        self.assertEqual(
            self.defaultValueNodeValue,
            self.defaultValueNode.defaultValue,
            "defaultValueNode.defaultValue is not %s" % self.defaultValueNodeValue,
            )


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
