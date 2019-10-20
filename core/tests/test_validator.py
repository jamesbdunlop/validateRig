import unittest
import logging
from const import serialization as c_serialization
from const import testData as c_testdata
import core.nodes as c_nodes
import core.validator as c_validator
logger = logging.getLogger(__name__)


class Test_Validator(unittest.TestCase):

    def setUp(self):
        self.sourceNodeName = c_testdata.SRC_NODENAME
        self.srcNodeAttrName = c_testdata.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testdata.SRC_ATTRVALUE

        self.ConnectionValidityNodeName = c_testdata.VALIDITY_NODENAME
        self.ConnectionValidityNodeAttrName = c_testdata.VALIDITY_ATTRNAME
        self.ConnectionValidityNodeAttrValue = c_testdata.VALIDITY_ATTRVALUE

        self.sourceNode = c_nodes.SourceNode(name=self.sourceNodeName)

        self.ConnectionValidityNode = c_nodes.ConnectionValidityNode(name=self.ConnectionValidityNodeName)
        self.ConnectionValidityNode.attributeName = self.ConnectionValidityNodeAttrName
        self.ConnectionValidityNode.attributeValue = self.ConnectionValidityNodeAttrValue
        self.ConnectionValidityNode.srcAttributeName = self.srcNodeAttrName
        self.ConnectionValidityNode.srcAttributeValue = self.srcNodeAttrValue

        self.sourceNode.addNodeToCheck(self.ConnectionValidityNode)

        self.validator = c_validator.Validator(name=c_testdata.VALIDATOR_NAME)

        self.expectedToData = {c_serialization.KEY_VALIDATOR_NAME: c_testdata.VALIDATOR_NAME,
                               c_serialization.KEY_VALIDATOR_NODES: [
                                   {
                                    c_serialization.KEY_NODENAME: self.sourceNodeName,
                                    c_serialization.KEY_NODTYPE: c_testdata.SRC_NODETYPE,
                                    c_serialization.KEY_VAILIDITYNODES: [
                                       {
                                        c_serialization.KEY_NODENAME: self.ConnectionValidityNodeName,
                                        c_serialization.KEY_NODTYPE: c_testdata.VALIDITY_NODETYPE,
                                        c_serialization.KEY_ATTRIBUTENAME: self.ConnectionValidityNodeAttrName,
                                        c_serialization.KEY_ATTRIBUTEVALUE: self.ConnectionValidityNodeAttrValue,
                                        c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                                        c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue
                                       }
                                    ],
                                   }
                               ]
                               }

    def test_validatorName(self):
        self.assertEqual(self.validator.name, c_testdata.VALIDATOR_NAME,
                         "ValidatorName is not %s" % c_testdata.VALIDATOR_NAME)

    def test_addSourceNode(self):
        self.assertEqual(True, self.validator.addNodeToValidate(self.sourceNode),
                         "Could not .addNodeToValidate?! Name already exists?")

    def test_validatorIterNodes(self):
        self.validator.addNodeToValidate(self.sourceNode)
        nodes = [n for n in self.validator.iterSourceNodes()]

        self.assertEqual(1, len(nodes),
                         "Nodes must be len 1! You have an empty list!")
        self.assertEqual(nodes[0], self.sourceNode,
                         "Validators [0] node is not %s" % self.sourceNode)

    def test_validatorToFileJSON(self):
        self.validator.addNodeToValidate(self.sourceNode)
        self.assertTrue(self.validator.to_fileJSON(filePath="C:/Temp/%s.json" % self.validator.name),
                        "Failed to write validator data to disk!")

    def test_validatorToData(self):
        self.validator.addNodeToValidate(self.sourceNode)
        self.assertEqual(self.expectedToData, self.validator.toData(),
                         "Validation toData does not match! %s %s" % (self.expectedToData, self.validator.toData()))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
