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

        self.ValidityNodeName = c_testData.VALIDITY_NODENAME
        self.ValidityNodeAttrName = c_testData.VALIDITY_ATTRNAME
        self.ValidityNodeAttrValue = c_testData.VALIDITY_ATTRVALUE

        # Nodes now
        self.sourceNode = c_nodes.SourceNode(name=self.sourceNodeName)

        self.ValidityNode = c_nodes.ValidityNode(name=self.ValidityNodeName)
        self.ValidityNode.attributeName = self.ValidityNodeAttrName
        self.ValidityNode.attributeValue = self.ValidityNodeAttrValue
        self.ValidityNode.srcAttributeName = self.srcNodeAttrName
        self.ValidityNode.srcAttributeValue = self.srcNodeAttrValue

        self.sourceNode.addNodeToCheck(self.ValidityNode)

        self.expectedToData = {
            c_serialization.KEY_NODENAME: self.sourceNodeName,
            c_serialization.KEY_DESTNODES: [{
                         c_serialization.KEY_NODENAME: self.ValidityNodeName,
                         c_serialization.KEY_ATTRIBUTENAME: self.ValidityNodeAttrName,
                         c_serialization.KEY_ATTRIBUTEVALUE: self.ValidityNodeAttrValue,
                         c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                         c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue,
                         }]
            }

    def test_instanceTypes(self):
        self.assertIsInstance(self.sourceNode, c_nodes.ValidationNode)

    def test_sourceNodeName(self):
        self.assertEqual(self.sourceNodeName, self.sourceNode.name,
                         "srcNodeName is not %s" % self.sourceNodeName)

    def test_ValidityNodeName(self):
        self.assertEqual(self.ValidityNodeName, self.ValidityNode.name,
                         "ValidityNodeName is not %s" % self.ValidityNodeName)

    def test_ValidityNode_attributeName(self):
        self.assertEqual(self.ValidityNodeAttrName, self.ValidityNode.attributeName,
                         "attributeName is not %s" % self.ValidityNodeAttrName)

    def test_ValidityNode_attributeValue(self):
        self.assertEqual(self.ValidityNodeAttrValue, self.ValidityNode.attributeValue,
                         "attributeValue is not %s" % self.ValidityNodeAttrValue)

    def test_ValidityNode_srcAttributeName(self):
        self.assertEqual(self.srcNodeAttrName, self.ValidityNode._srcAttributeName,
                         "srcAttributeName is not %s" % self.srcNodeAttrName)

    def test_ValidityNode_srcAttributeValue(self):
        self.assertEqual(self.srcNodeAttrValue, self.ValidityNode.srcAttributeValue,
                         "srcAttributeValue is not %s" % self.srcNodeAttrValue)

    def test_srcNode_iterNodes(self):
        nodes = [n for n in self.sourceNode.iterNodes()]

        self.assertEqual(len(nodes), 1,
                         "Length of itrNodes is not 1!")
        self.assertEqual(nodes[0], self.ValidityNode,
                         "[0] Node is not %s" % self.ValidityNode)

    def test_sourceNode_toData(self):
        self.assertEqual(self.sourceNode.toData(), self.expectedToData,
                         "%s doesn't match! %s" % (self.sourceNode.toData(), self.expectedToData))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
