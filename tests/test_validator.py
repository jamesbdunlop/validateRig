#  Copyright (c) 2019.  James Dunlop

import unittest
import logging
from const import serialization as c_serialization
from const import testData as c_testdata
import core.nodes as c_nodes
import core.validator as c_validator

logger = logging.getLogger(__name__)


class Test_Validator(unittest.TestCase):
    def setUp(self):
        self.validator = c_validator.createValidator(name=c_testdata.VALIDATOR_NAME)

        self.sourceNodeName = c_testdata.SRC_NODENAME
        self.srcNodeAttrName = c_testdata.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testdata.SRC_ATTRVALUE

        self.connectionValidityNodeName = c_testdata.VALIDITY_NODENAME
        self.connectionValidityNodeAttrName = c_testdata.VALIDITY_DEST_ATTRNAME
        self.connectionValidityNodeAttrValue = c_testdata.VALIDITY_DEST_ATTRVALUE

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

        self.sourceNode.addChild(self.connectionValidityNode)

        # Add the sourceNode to the validator now
        self.validator.addSourceNode(self.sourceNode)

        self.expectedToData = {
            c_serialization.KEY_VALIDATOR_NAME: c_testdata.VALIDATOR_NAME,
            c_serialization.KEY_VALIDATOR_NODES: [
                {
                    c_serialization.KEY_NODENAME: self.sourceNodeName,
                    c_serialization.KEY_NODELONGNAME: self.sourceNodeName,
                    c_serialization.KEY_NODEDISPLAYNAME: self.sourceNodeName,
                    c_serialization.KEY_NODENAMESPACE: "",
                    c_serialization.KEY_NODETYPE: c_testdata.SRC_NODETYPE,
                    c_serialization.KEY_VAILIDITYNODES: [
                        {
                            c_serialization.KEY_NODENAME: self.connectionValidityNodeName,
                            c_serialization.KEY_NODELONGNAME: self.connectionValidityNodeName,
                            c_serialization.KEY_NODEDISPLAYNAME: self.connectionValidityNodeName,
                            c_serialization.KEY_NODENAMESPACE: "",
                            c_serialization.KEY_NODETYPE: c_testdata.VALIDITY_NODETYPE,
                            c_serialization.KEY_DEST_ATTRIBUTENAME: self.connectionValidityNodeAttrName,
                            c_serialization.KEY_DEST_ATTRIBUTEVALUE: self.connectionValidityNodeAttrValue,
                            c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                            c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue,
                        }
                    ],
                }
            ],
        }

    def test_instanceTypes(self):
        self.assertIsInstance(self.validator, c_validator.Validator)

    def test_setters(self):
        testName = "FART"
        self.validator.name = testName
        self.assertEqual(
            self.validator.name,
            testName,
            "ValidatorName is not %s" % testName,
        )

        testNameSpace = "FARTED"
        self.validator.namespace = testNameSpace
        self.assertEqual(
            self.validator.namespace,
            testNameSpace,
            "ValidatorName is not %s" % testNameSpace,
        )

        testStatus = "FAILUREWILLROBINSON"
        self.validator.status = testStatus
        self.assertEqual(
            self.validator.status,
            testStatus,
            "ValidatorName is not %s" % testStatus,
        )

    def test_validationFailed(self):
        self.assertFalse(self.validator.failed)

    def test_validationPassed(self):
        self.assertTrue(self.validator.passed)

    def test_sourceNodeLongNameExists(self):
        self.assertTrue(self.validator.sourceNodeLongNameExists(self.sourceNodeName))

    def test_Name(self):
        self.assertEqual(
            self.validator.name,
            c_testdata.VALIDATOR_NAME,
            "ValidatorName is not %s" % c_testdata.VALIDATOR_NAME,
        )

    def test_addSourceNode(self):
        nodeName = "2ndSourceNode"
        srcNode = c_nodes.SourceNode(name=nodeName, longName=nodeName)

        self.assertTrue(
            self.validator.addSourceNode(srcNode), "validator.addSourceNode failed!",
        )

        self.assertTrue(
            self.validator.addSourceNode(srcNode, force=True), "validator.addSourceNode failed!",
        )

        with self.assertRaises(IndexError) as context:
            self.validator.addSourceNode(srcNode, force=False)
        self.assertTrue('Use force=True if you want to overwrite existing!' in str(context.exception))

    def test_addSourceNodeFromData(self):
        nodeName = "3rdSourceNode"
        srcNode = c_nodes.SourceNode(name=nodeName, longName=nodeName)
        data = srcNode.toData()
        self.validator.addSourceNodeFromData(data)
        self.assertTrue(
            self.validator.sourceNodeExists(srcNode), "validator.addSourceNode failed!",
        )

    def test_removeSourceNode(self):
        nodeName = "toRemove"
        tmpSourceNode = c_nodes.SourceNode(name=nodeName, longName=nodeName)
        self.validator.addSourceNode(tmpSourceNode)
        self.assertTrue(
            self.validator.removeSourceNode(tmpSourceNode),
            "Failed to remove tmpSourceNode!",
        )

        self.assertFalse(
            self.validator.removeSourceNode(tmpSourceNode),
            "Removed tmpSourceNode which shouldn't be in the validator anymore!!",
        )

    def test_replaceExistingSourceNode(self):
        self.assertTrue(
            self.validator.replaceExistingSourceNode(self.sourceNode),
            "Failed to replaceExistingSourceNode!",
        )

    def test_findSourceNodeByLongName(self):
        sourceNode = self.validator.findSourceNodeByLongName(name=self.sourceNodeName)
        self.assertEqual(
            sourceNode,
            self.sourceNode,
            "self.validator.findSourceNodeByLongName() is not self.sourceNode!",
        )

    def test_sourceNodeExists(self):
        self.assertEqual(
            True,
            self.validator.sourceNodeExists(self.sourceNode),
            "SourceNode doesn't exist!",
        )

    def test_iterSourceNodes(self):
        nodes = [n for n in self.validator.iterSourceNodes()]

        self.assertEqual(1, len(nodes), "Nodes must be len 1!")
        self.assertEqual(
            nodes[0], self.sourceNode, "Validators [0] node is not %s" % self.sourceNode
        )

    def test_toFileJSON(self):
        self.assertTrue(
            self.validator.to_fileJSON(
                filePath="C:/Temp/%s.json" % self.validator.name
            ),
            "Failed to write validator data to disk!",
        )

    def test_toData(self):
        self.assertEqual(
            self.expectedToData,
            self.validator.toData(),
            "Validation toData does not match! %s %s"
            % (self.expectedToData, self.validator.toData()),
        )


if __name__ == "__main__":# pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
