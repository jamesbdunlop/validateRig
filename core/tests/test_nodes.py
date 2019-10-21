import unittest
import logging
from const import serialization as c_serialization
from const import testData as c_testData
import core.nodes as c_nodes
logger = logging.getLogger(__name__)


class Test_Nodes(unittest.TestCase):

    def setUp(self):
        # Names locally etc
        self.sourceNodeName = c_testData.SRC_NODENAME
        self.srcNodeAttrName = c_testData.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testData.SRC_ATTRVALUE
        self.sourceNodeType = c_testData.SRC_NODETYPE

        self.connectionValidityNodeName = c_testData.VALIDITY_NODENAME
        self.connectionValidityNodeAttrName = c_testData.VALIDITY_ATTRNAME
        self.connectionValidityNodeAttrValue = c_testData.VALIDITY_ATTRVALUE
        self.connectionValidityNodeType = c_testData.VALIDITY_NODETYPE

        # Nodes now
        self.sourceNode = c_nodes.SourceNode(name=self.sourceNodeName)

        self.connectionValidityNode = c_nodes.connectionValidityNode(name=self.connectionValidityNodeName)
        self.connectionValidityNode.attributeName = self.connectionValidityNodeAttrName
        self.connectionValidityNode.attributeValue = self.connectionValidityNodeAttrValue
        self.connectionValidityNode.srcAttributeName = self.srcNodeAttrName
        self.connectionValidityNode.srcAttributeValue = self.srcNodeAttrValue

        self.sourceNode.addValidityNode(self.connectionValidityNode)

        self.expectedToData = {
            c_serialization.KEY_NODENAME: self.sourceNodeName,
            c_serialization.KEY_NODTYPE: self.sourceNodeType,
            c_serialization.KEY_VAILIDITYNODES: [{
                         c_serialization.KEY_NODENAME: self.connectionValidityNodeName,
                         c_serialization.KEY_NODTYPE: self.connectionValidityNodeType,
                         c_serialization.KEY_ATTRIBUTENAME: self.connectionValidityNodeAttrName,
                         c_serialization.KEY_ATTRIBUTEVALUE: self.connectionValidityNodeAttrValue,
                         c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                         c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue,
                         }]
            }

    def test_instanceTypes(self):
        self.assertIsInstance(self.sourceNode, c_nodes.ValidationNode)

    def test_sourceNodeName(self):
        self.assertEqual(self.sourceNodeName, self.sourceNode.name,
                         "srcNodeName is not %s" % self.sourceNodeName)

    def test_connectionValidityNodeName(self):
        self.assertEqual(self.connectionValidityNodeName, self.connectionValidityNode.name,
                         "connectionValidityNodeName is not %s" % self.connectionValidityNodeName)

    def test_connectionValidityNode_attributeName(self):
        self.assertEqual(self.connectionValidityNodeAttrName, self.connectionValidityNode.attributeName,
                         "attributeName is not %s" % self.connectionValidityNodeAttrName)

    def test_connectionValidityNode_attributeValue(self):
        self.assertEqual(self.connectionValidityNodeAttrValue, self.connectionValidityNode.attributeValue,
                         "attributeValue is not %s" % self.connectionValidityNodeAttrValue)

    def test_connectionValidityNode_srcAttributeName(self):
        self.assertEqual(self.srcNodeAttrName, self.connectionValidityNode._srcAttributeName,
                         "srcAttributeName is not %s" % self.srcNodeAttrName)

    def test_connectionValidityNode_srcAttributeValue(self):
        self.assertEqual(self.srcNodeAttrValue, self.connectionValidityNode.srcAttributeValue,
                         "srcAttributeValue is not %s" % self.srcNodeAttrValue)

    def test_srcNode_iterValidityNodes(self):
        nodes = [n for n in self.sourceNode.iterValidityNodes()]

        self.assertEqual(len(nodes), 1,
                         "Length of itrNodes is not 1!")
        self.assertEqual(nodes[0], self.connectionValidityNode,
                         "[0] Node is not %s" % self.connectionValidityNode)

    def test_sourceNode_toData(self):
        self.assertEqual(self.sourceNode.toData(), self.expectedToData,
                         "%s doesn't match! %s" % (self.sourceNode.toData(), self.expectedToData))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
