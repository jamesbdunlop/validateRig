import unittest
import logging
from constants import serialization as c_serialization
from constants import testData as c_testData
import core.nodes as c_nodes
logger = logging.getLogger(__name__)


class Test_Nodes(unittest.TestCase):

    def setUp(self):
        # Names locally etc
        self.sourceNodeName = c_testData.SRC_NODENAME
        self.srcNodeAttrName = c_testData.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testData.SRC_ATTRVALUE

        self.ConnectionValidityNodeName = c_testData.VALIDITY_NODENAME
        self.ConnectionValidityNodeAttrName = c_testData.VALIDITY_ATTRNAME
        self.ConnectionValidityNodeAttrValue = c_testData.VALIDITY_ATTRVALUE

        # Nodes now
        self.sourceNode = c_nodes.SourceNode(name=self.sourceNodeName)

        self.ConnectionValidityNode = c_nodes.ConnectionValidityNode(name=self.ConnectionValidityNodeName)
        self.ConnectionValidityNode.attributeName = self.ConnectionValidityNodeAttrName
        self.ConnectionValidityNode.attributeValue = self.ConnectionValidityNodeAttrValue
        self.ConnectionValidityNode.srcAttributeName = self.srcNodeAttrName
        self.ConnectionValidityNode.srcAttributeValue = self.srcNodeAttrValue

        self.sourceNode.addNodeToCheck(self.ConnectionValidityNode)

        self.expectedToData = {
            c_serialization.KEY_NODENAME: self.sourceNodeName,
            c_serialization.KEY_VAILIDITYNODES: [{
                         c_serialization.KEY_NODENAME: self.ConnectionValidityNodeName,
                         c_serialization.KEY_ATTRIBUTENAME: self.ConnectionValidityNodeAttrName,
                         c_serialization.KEY_ATTRIBUTEVALUE: self.ConnectionValidityNodeAttrValue,
                         c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                         c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue,
                         }]
            }

    def test_instanceTypes(self):
        self.assertIsInstance(self.sourceNode, c_nodes.ValidationNode)

    def test_sourceNodeName(self):
        self.assertEqual(self.sourceNodeName, self.sourceNode.name,
                         "srcNodeName is not %s" % self.sourceNodeName)

    def test_ConnectionValidityNodeName(self):
        self.assertEqual(self.ConnectionValidityNodeName, self.ConnectionValidityNode.name,
                         "ConnectionValidityNodeName is not %s" % self.ConnectionValidityNodeName)

    def test_ConnectionValidityNode_attributeName(self):
        self.assertEqual(self.ConnectionValidityNodeAttrName, self.ConnectionValidityNode.attributeName,
                         "attributeName is not %s" % self.ConnectionValidityNodeAttrName)

    def test_ConnectionValidityNode_attributeValue(self):
        self.assertEqual(self.ConnectionValidityNodeAttrValue, self.ConnectionValidityNode.attributeValue,
                         "attributeValue is not %s" % self.ConnectionValidityNodeAttrValue)

    def test_ConnectionValidityNode_srcAttributeName(self):
        self.assertEqual(self.srcNodeAttrName, self.ConnectionValidityNode._srcAttributeName,
                         "srcAttributeName is not %s" % self.srcNodeAttrName)

    def test_ConnectionValidityNode_srcAttributeValue(self):
        self.assertEqual(self.srcNodeAttrValue, self.ConnectionValidityNode.srcAttributeValue,
                         "srcAttributeValue is not %s" % self.srcNodeAttrValue)

    def test_srcNode_iterNodes(self):
        nodes = [n for n in self.sourceNode.iterNodes()]

        self.assertEqual(len(nodes), 1,
                         "Length of itrNodes is not 1!")
        self.assertEqual(nodes[0], self.ConnectionValidityNode,
                         "[0] Node is not %s" % self.ConnectionValidityNode)

    def test_sourceNode_toData(self):
        self.assertEqual(self.sourceNode.toData(), self.expectedToData,
                         "%s doesn't match! %s" % (self.sourceNode.toData(), self.expectedToData))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
