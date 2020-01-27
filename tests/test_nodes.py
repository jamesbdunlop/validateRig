#  Copyright (c) 2019.  James Dunlop

import unittest
import logging

from validateRig.const import testData as vrc_testData
from validateRig.const import serialization as vrconst_serialization
from validateRig.core import nodes as vrc_nodes

logger = logging.getLogger(__name__)


class Test_Nodes(unittest.TestCase):
    def setUp(self):
        self.nodeName = vrc_testData.NODENAME
        self.nodeNameSpace = "myNameSpace"
        self.nodeLongName = "|{}:{}".format(self.nodeNameSpace, self.nodeName)
        self.newNamespace = "fart"
        self.newNodeLongName = "|{}:{}".format(self.newNamespace, self.nodeName)

        self.baseNode = vrc_nodes.Node(name=self.nodeName, longName=self.nodeLongName)
        #######################################
        self.sourceNodeName = vrc_testData.SRC_NODENAME
        self.srcNodeAttrName = vrc_testData.SRC_ATTRNAME
        self.srcNodeAttrValue = vrc_testData.SRC_ATTRVALUE
        self.sourceNode = vrc_nodes.SourceNode(
            name=self.sourceNodeName, longName=self.sourceNodeName
        )
        #######################################
        self.connectionValidityNodeName = vrc_testData.VALIDITY_NODENAME
        self.connectionValidityNodeType = vrc_testData.VALIDITY_NODETYPE

        self.connectionValidityNode = vrc_nodes.ConnectionValidityNode(
            name=self.connectionValidityNodeName,
            longName=self.connectionValidityNodeName,
        )
        self.connectionValidityNode.connectionData = {}

        #######################################
        self.defaultValueNodeName = vrc_testData.DEFAULT_NODENAME
        self.defaultValueNodeValue = vrc_testData.DEFAULT_NODEVALUE
        self.defaultValueNodeType = vrc_testData.DEFAULT_NODETYPE

        self.defaultValueNode = vrc_nodes.DefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
        )
        self.defaultValueNode.defaultValueData = {}

        self.sourceNode.addChild(self.connectionValidityNode)
        self.sourceNode.addChild(self.defaultValueNode)

        self.expectedToData = {
            vrconst_serialization.KEY_NODENAME: self.sourceNodeName,
            vrconst_serialization.KEY_NODELONGNAME: self.sourceNodeName,
            vrconst_serialization.KEY_NODETYPE: vrc_testData.SRC_NODETYPE,
            vrconst_serialization.KEY_NODEDISPLAYNAME: self.sourceNodeName,
            vrconst_serialization.KEY_VAILIDITYNODES: [
                {
                    vrconst_serialization.KEY_NODENAME: self.connectionValidityNodeName,
                    vrconst_serialization.KEY_NODELONGNAME: self.connectionValidityNodeName,
                    vrconst_serialization.KEY_NODETYPE: self.connectionValidityNodeType,
                    vrconst_serialization.KEY_NODEDISPLAYNAME: self.connectionValidityNodeName,
                    vrconst_serialization.KEY_CONNDATA: {},
                },
                {
                    vrconst_serialization.KEY_NODENAME: self.defaultValueNodeName,
                    vrconst_serialization.KEY_NODELONGNAME: self.defaultValueNodeName,
                    vrconst_serialization.KEY_NODETYPE: self.defaultValueNodeType,
                    vrconst_serialization.KEY_NODEDISPLAYNAME: self.defaultValueNodeName,
                    vrconst_serialization.KEY_DEFAULTVALUEDATA: {},
                },
            ],
        }

    ## GENEERIC NODE
    def test_instanceTypes(self):
        self.assertIsInstance(self.sourceNode, vrc_nodes.Node)
        self.assertIsInstance(self.defaultValueNode, vrc_nodes.DefaultValueNode)
        self.assertIsInstance(
            self.connectionValidityNode, vrc_nodes.ConnectionValidityNode
        )

    def test_node_fromData(self):
        newNode = vrc_nodes.Node.fromData(self.expectedToData)
        self.assertIsInstance(newNode, vrc_nodes.Node)

    def test_node_name(self):
        self.assertEqual(
            self.nodeName,
            self.baseNode.name,
            "baseNode.name is not %s" % self.nodeName,
        )

    def test_node_removeChild(self):
        children = list(self.sourceNode.iterChildren())
        self.sourceNode.removeChild(self.defaultValueNode)
        self.assertNotEqual(children, self.sourceNode.children, "Child remove failed!")

    def test_node_setters(self):
        testName = "TESTName"
        self.baseNode.name = testName
        self.assertEqual(
            testName, self.baseNode.name, "baseNode.name is not %s" % testName,
        )

        self.baseNode.displayName = testName
        self.assertEqual(
            testName,
            self.baseNode.displayName,
            "baseNode.displayName is not %s" % testName,
        )

        self.baseNode.longName = testName
        self.assertEqual(
            testName, self.baseNode.longName, "baseNode.longName is not %s" % testName,
        )

        testStatus = "Failed"
        self.baseNode.status = testStatus
        self.assertEqual(
            testStatus, self.baseNode.status, "baseNode.status is not %s" % testStatus,
        )

        self.baseNode.nameSpace = self.nodeNameSpace
        self.assertEqual(
            self.nodeNameSpace,
            self.baseNode.nameSpace,
            "baseNode.nameSpace is not %s" % self.nodeNameSpace,
        )

    def test_node_parent(self):
        self.assertEqual(
            self.defaultValueNode.parent,
            self.sourceNode,
            "defaultValueNode's parent is not sourceNode!",
        )

    ## SOURCE NODE SPECIFIC
    def test_sourceNode_name(self):
        self.assertEqual(
            self.sourceNodeName,
            self.sourceNode.name,
            "srcNodeName is not %s" % self.sourceNodeName,
        )

    def test_sourceNode_iterDescendants(self):
        descendants = list(self.sourceNode.iterDescendants())
        currentDescendants = [self.connectionValidityNode, self.defaultValueNode]
        self.assertEqual(
            currentDescendants, descendants, "iterDescendants doesn't match!"
        )

    def test_sourceNode_iterChildren(self):
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

    def test_sourceNode_fromData(self):
        newSourceNode = vrc_nodes.SourceNode.fromData(self.expectedToData)
        self.assertIsInstance(newSourceNode, vrc_nodes.SourceNode)

        with self.assertRaises(KeyError) as context:
            c = vrc_nodes.SourceNode.fromData({})
        self.assertTrue(
            "NoneType is not a valid sourceNodeName!" in str(context.exception)
        )

    def test_sourceNode_toData(self):
        self.assertEqual(
            self.sourceNode.toData(),
            self.expectedToData,
            "%s doesn't match! %s" % (self.sourceNode.toData(), self.expectedToData),
        )

    ## CONNECTION NODE SPECIFIC
    def test_connectionValidityNode_name(self):
        self.assertEqual(
            self.connectionValidityNodeName,
            self.connectionValidityNode.name,
            "connectionValidityNodeName is not %s" % self.connectionValidityNodeName,
        )

    ## DEFAULTVALUE NODE SPECIFIC
    def test_defaultValueNode_name(self):
        self.assertEqual(
            self.defaultValueNodeName,
            self.defaultValueNode.name,
            "defaultValueNode.name is not %s" % self.defaultValueNodeName,
        )


if __name__ == "__main__":  # pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
