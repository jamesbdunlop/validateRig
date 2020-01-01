#  Copyright (c) 2019.  James Dunlop

import unittest
import logging
from const import serialization as c_serialization
from const import testData as c_testData
import core.nodes as c_nodes

logger = logging.getLogger(__name__)
# TODO set status tests and anything else missing from base node


class Test_Nodes(unittest.TestCase):
    def setUp(self):
        self.nodeName = c_testData.NODENAME
        self.nodeNameSpace = "myNameSpace"
        self.nodeLongName = "|{}:{}".format(self.nodeNameSpace,self.nodeName)
        self.newNamespace = "fart"
        self.newNodeLongName = "|{}:{}".format(self.newNamespace,self.nodeName)

        self.baseNode = c_nodes.Node(name=self.nodeName, longName=self.nodeLongName)
        #######################################
        self.sourceNodeName = c_testData.SRC_NODENAME
        self.srcNodeAttrName = c_testData.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testData.SRC_ATTRVALUE
        self.sourceNode = c_nodes.SourceNode(
            name=self.sourceNodeName, longName=self.sourceNodeName
        )
        #######################################
        self.connectionValidityNodeName = c_testData.VALIDITY_NODENAME
        self.connectionValidityNodeAttrName = c_testData.VALIDITY_DEST_ATTRNAME
        self.connectionValidityNodeAttrValue = c_testData.VALIDITY_DEST_ATTRVALUE
        self.connectionValidityNodeType = c_testData.VALIDITY_NODETYPE
        self.connectionValidityNode = c_nodes.ConnectionValidityNode(
            name=self.connectionValidityNodeName,
            longName=self.connectionValidityNodeName,
        )
        self.connectionValidityNode.destAttrName = self.connectionValidityNodeAttrName
        self.connectionValidityNode.destAttrValue = self.connectionValidityNodeAttrValue
        self.connectionValidityNode.srcAttrName = self.srcNodeAttrName
        self.connectionValidityNode.srcAttrValue = self.srcNodeAttrValue
        #######################################
        self.defaultValueNodeName = c_testData.DEFAULT_NODENAME
        self.defaultValueNodeValue = c_testData.DEFAULT_NODEVALUE
        self.defaultValueNodeType = c_testData.DEFAULT_NODETYPE
        self.defaultValueNode = c_nodes.DefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
            defaultValue=self.defaultValueNodeValue,
        )

        self.sourceNode.addChild(self.connectionValidityNode)
        self.sourceNode.addChild(self.defaultValueNode)

        self.expectedToData = {
            c_serialization.KEY_NODENAME: self.sourceNodeName,
            c_serialization.KEY_NODELONGNAME: self.sourceNodeName,
            c_serialization.KEY_NODETYPE: c_testData.SRC_NODETYPE,
            c_serialization.KEY_NODEDISPLAYNAME: self.sourceNodeName,
            c_serialization.KEY_NODENAMESPACE: "",
            c_serialization.KEY_VAILIDITYNODES: [
                {
                    c_serialization.KEY_NODENAME: self.connectionValidityNodeName,
                    c_serialization.KEY_NODELONGNAME: self.connectionValidityNodeName,
                    c_serialization.KEY_NODETYPE: self.connectionValidityNodeType,
                    c_serialization.KEY_NODEDISPLAYNAME: self.connectionValidityNodeName,
                    c_serialization.KEY_NODENAMESPACE: "",
                    c_serialization.KEY_DEST_ATTRIBUTENAME: self.connectionValidityNodeAttrName,
                    c_serialization.KEY_DEST_ATTRIBUTEVALUE: self.connectionValidityNodeAttrValue,
                    c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                    c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue,
                },
                {
                    c_serialization.KEY_NODENAME: self.defaultValueNodeName,
                    c_serialization.KEY_NODELONGNAME: self.defaultValueNodeName,
                    c_serialization.KEY_NODETYPE: self.defaultValueNodeType,
                    c_serialization.KEY_NODEDISPLAYNAME: self.defaultValueNodeName,
                    c_serialization.KEY_NODENAMESPACE: "",
                    c_serialization.KEY_DEFAULTVALUE: self.defaultValueNodeValue,
                },
            ],
        }

    ## GENEERIC NODE
    def test_instanceTypes(self):
        self.assertIsInstance(self.sourceNode, c_nodes.Node)
        self.assertIsInstance(self.defaultValueNode, c_nodes.DefaultValueNode)
        self.assertIsInstance(
            self.connectionValidityNode, c_nodes.ConnectionValidityNode
        )

    def test_node_fromData(self):
        newNode = c_nodes.Node.fromData(self.expectedToData)
        self.assertIsInstance(newNode, c_nodes.Node)

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

    def test_node_setNameSpaceInDisplayName(self):
        self.baseNode.nameSpace = self.nodeNameSpace
        namespacedname = "{}:{}".format(self.baseNode.nameSpace, self.baseNode.name)
        self.baseNode.setNameSpaceInDisplayName(show=True)
        displayName = self.baseNode.displayName
        self.assertEqual(
            namespacedname, displayName, "{} != {}".format(namespacedname, displayName)
        )

        self.baseNode.setNameSpaceInDisplayName(show=False)
        nodeName = self.baseNode.name
        displayName = self.baseNode.displayName
        self.assertEqual(
            nodeName, displayName, "{} != {}".format(nodeName, displayName)
        )

    def test_node_setLongNameInDisplayName(self):
        self.baseNode.setLongNameInDisplayName(show=True)
        self.assertEqual(self.baseNode.displayName, self.baseNode.longName)

        self.baseNode.setLongNameInDisplayName(show=False)
        self.assertEqual(self.baseNode.name, self.baseNode.displayName)

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
        newSourceNode = c_nodes.SourceNode.fromData(self.expectedToData)
        self.assertIsInstance(newSourceNode, c_nodes.SourceNode)

        with self.assertRaises(KeyError) as context:
            c = c_nodes.SourceNode.fromData({})
        self.assertTrue('NoneType is not a valid sourceNodeName!' in str(context.exception))

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
            self.connectionValidityNode.srcAttrName,
            "srcAttrName is not %s" % self.srcNodeAttrName,
        )

    def test_connectionValidityNode_srcAttrValue(self):
        self.assertEqual(
            self.srcNodeAttrValue,
            self.connectionValidityNode.srcAttrValue,
            "srcAttrValue is not %s" % self.srcNodeAttrValue,
        )

    def test_connectionValidityNode_namespaceChanges(self):
        ns = "FuckingNameSpaces"
        self.connectionValidityNode.nameSpace = ns
        self.connectionValidityNode.setNameSpaceInDisplayName(True)
        nsName = "{}:{}".format(ns, self.connectionValidityNode.name)
        self.assertEqual(nsName, self.connectionValidityNode.displayName)

    ## DEFAULTVALUE NODE SPECIFIC
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

        self.defaultValueNode.defaultValue = None
        self.assertEqual(
            None,
            self.defaultValueNode.defaultValue,
            "defaultValueNode.defaultValue is not None!",
        )


if __name__ == "__main__":  # pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
