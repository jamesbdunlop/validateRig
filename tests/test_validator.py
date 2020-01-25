#  Copyright (c) 2019.  James Dunlop

import unittest
import logging
from const import serialization as c_serialization
from const import testData as c_testdata
import core.nodes as c_nodes
import core.validator as c_validator
import core.factory as c_factory

logger = logging.getLogger(__name__)


class Test_Validator(unittest.TestCase):
    def setUp(self):
        self.validator = c_factory.createValidator(
            name=c_testdata.VALIDATOR_NAME, nameSpace=c_testdata.VALIDATOR_NAMESPACE, data=None
        )

        self.sourceNodeName = c_testdata.SRC_NODENAME
        self.sourceNodeLongName = "|{}:{}".format(c_testdata.VALIDATOR_NAMESPACE, self.sourceNodeName)
        self.sourceNode = c_nodes.SourceNode(name=self.sourceNodeName, longName=self.sourceNodeLongName)


        connData = {
                "srcData": {
                    "attrName": "testConnSrcAttrName",
                    "plugData": [[False, False, "", 0], ],
                },
                "destData": {
                    "nodeName": "testDestNodeName",
                    "plugData": {"testAttrName": 666},
                }

            }
        self.connectionNodeName = c_testdata.VALIDITY_NODENAME
        self.connectionNodeLongName = "|{}:{}".format(c_testdata.VALIDATOR_NAMESPACE, c_testdata.VALIDITY_NODENAME)
        self.connectionValidityNode = c_nodes.ConnectionValidityNode(name=self.connectionNodeName,
                                                                     longName=self.connectionNodeLongName)

        self.connectionValidityNode.connectionData = connData

        self.sourceNode.addChild(self.connectionValidityNode)

        # Add the sourceNode to the validator now
        self.validator.addSourceNode(self.sourceNode)

        self.expectedToData = {
            c_serialization.KEY_VALIDATOR_NAME: c_testdata.VALIDATOR_NAME,
            c_serialization.KEY_VALIDATORNAMESPACE: c_testdata.VALIDATOR_NAMESPACE,
            c_serialization.KEY_VALIDATOR_NODES: [
                {
                    c_serialization.KEY_NODENAME: self.sourceNodeName,
                    c_serialization.KEY_NODELONGNAME: self.sourceNodeLongName,
                    c_serialization.KEY_NODEDISPLAYNAME: self.sourceNodeName,
                    c_serialization.KEY_NODETYPE: c_testdata.SRC_NODETYPE,
                    c_serialization.KEY_VAILIDITYNODES: [
                        {
                            c_serialization.KEY_NODENAME: self.connectionNodeName,
                            c_serialization.KEY_NODELONGNAME: self.connectionNodeLongName,
                            c_serialization.KEY_NODEDISPLAYNAME: self.connectionNodeName,
                            c_serialization.KEY_NODETYPE: c_testdata.VALIDITY_NODETYPE,
                            c_serialization.KEY_CONNDATA: connData,
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
            self.validator.name, testName, "ValidatorName is not %s" % testName,
        )

        testNameSpace = "FARTED"
        self.validator.nameSpace = testNameSpace
        self.assertEqual(
            self.validator.nameSpace,
            testNameSpace,
            "ValidatorName is not %s" % testNameSpace,
        )

        testStatus = "FAILUREWILLROBINSON"
        self.validator.status = testStatus
        self.assertEqual(
            self.validator.status, testStatus, "ValidatorName is not %s" % testStatus,
        )

    def test_validationFailed(self):
        self.assertTrue(self.validator.failed)

    def test_validationPassed(self):
        self.assertFalse(self.validator.passed)

    def test_sourceNodeLongNameExists(self):
        self.assertTrue(
            self.validator.sourceNodeLongNameExists(self.sourceNodeLongName)
        )

    def test_Name(self):
        self.assertEqual(
            self.validator.name,
            c_testdata.VALIDATOR_NAME,
            "ValidatorName: %s is not %s"
            % (self.validator.name, c_testdata.VALIDATOR_NAME),
        )

    def test_namespaceOnCreate(self):
        self.assertEqual(
            c_testdata.VALIDATOR_NAMESPACE,
            self.validator.nameSpaceOnCreate,
            "_nameSpaceOnCreate: {} is not what it should be: {}".format(
                self.validator.nameSpaceOnCreate, c_testdata.VALIDATOR_NAMESPACE
            ),
        )

    def test_toggleLongNodeNames(self):
        self.validator.toggleLongNodeNames(True)
        srcNode = list(self.validator.iterSourceNodes())[0]
        self.assertEqual(srcNode.displayName, srcNode.longName)

        self.validator.toggleLongNodeNames(False)
        srcNode = list(self.validator.iterSourceNodes())[0]

        self.assertEqual(
            srcNode.displayName,
            "{}:{}".format(c_testdata.VALIDATOR_NAMESPACE, srcNode.name),
        )

    def test_updateNameSpaceInLongName(self):
        currentNamspace = self.validator.nameSpace
        newNamespace = "fartyblartfast"
        self.validator.nameSpace = newNamespace
        self.validator.updateNameSpaceInLongName(nameSpace=currentNamspace)
        srcNode = list(self.validator.iterSourceNodes())[0]
        result = newNamespace in srcNode.longName
        self.assertTrue(result)

    def test_addSourceNode(self):
        nodeName = "2ndSourceNode"
        srcNode = c_nodes.SourceNode(name=nodeName, longName=nodeName)

        self.assertTrue(
            self.validator.addSourceNode(srcNode), "validator.addSourceNode failed!",
        )

        self.assertTrue(
            self.validator.addSourceNode(srcNode, force=True),
            "validator.addSourceNode failed!",
        )

        with self.assertRaises(IndexError) as context:
            self.validator.addSourceNode(srcNode, force=False)
        self.assertTrue(
            "Use force=True if you want to overwrite existing!"
            in str(context.exception)
        )

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

        srcN = c_nodes.SourceNode("Idontexist", "|fart:Idontexist")
        self.assertFalse(
            self.validator.sourceNodeExists(srcN),
            "Apparent Idontexist sourceNode exists?! It should not!",
        )

    def test_addSourceNodes(self):
        tmp01 = c_nodes.SourceNode(
            "Src1", "|{}:Src1".format(c_serialization.KEY_VALIDATORNAMESPACE)
        )
        tmp02 = c_nodes.SourceNode(
            "Src2", "|{}:Src2".format(c_serialization.KEY_VALIDATORNAMESPACE)
        )
        srcNodes = [tmp01, tmp02]
        self.assertTrue(
            self.validator.addSourceNodes(srcNodes),
            "addSourceNodes didn't return True? It failed :(",
        )

    def test_findSourceNodeByLongName(self):
        sourceNode = self.validator.findSourceNodeByLongName(
            longName=self.sourceNodeLongName
        )
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


if __name__ == "__main__":  # pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
