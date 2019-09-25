import unittest
import logging
from constants import serialization as c_serialization
from constants import testData as c_testdata
import core.nodes as c_nodes
import core.validator as c_validator
logger = logging.getLogger(__name__)


class Test_Validator(unittest.TestCase):

    def setUp(self):
        self.sourceNodeName = c_testdata.SRC_NODENAME
        self.srcNodeAttrName = c_testdata.SRC_ATTRNAME
        self.srcNodeAttrValue = c_testdata.SRC_ATTRVALUE

        self.ValidityNodeName = c_testdata.VALIDITY_NODENAME
        self.ValidityNodeAttrName = c_testdata.VALIDITY_ATTRNAME
        self.ValidityNodeAttrValue = c_testdata.VALIDITY_ATTRVALUE

        self.sourceNode = c_nodes.SourceNode(name=self.sourceNodeName)

        self.ValidityNode = c_nodes.ValidityNode(name=self.ValidityNodeName)
        self.ValidityNode.attributeName = self.ValidityNodeAttrName
        self.ValidityNode.attributeValue = self.ValidityNodeAttrValue
        self.ValidityNode.srcAttributeName = self.srcNodeAttrName
        self.ValidityNode.srcAttributeValue = self.srcNodeAttrValue

        self.sourceNode.addNodeToCheck(self.ValidityNode)

        self.validator = c_validator.Validator(name=c_testdata.VALIDATOR_NAME)

        self.expectedToData = {c_serialization.KEY_VALIDATOR_NAME: c_testdata.VALIDATOR_NAME,
                               c_serialization.KEY_VALIDATOR_SOURCENODES: [
                                   {c_serialization.KEY_DESTNODES: [
                                       {
                                        c_serialization.KEY_NODENAME: self.ValidityNodeName,
                                        c_serialization.KEY_ATTRIBUTENAME: self.ValidityNodeAttrName,
                                        c_serialization.KEY_ATTRIBUTEVALUE: self.ValidityNodeAttrValue,
                                        c_serialization.KEY_SRC_ATTRIBUTENAME: self.srcNodeAttrName,
                                        c_serialization.KEY_SRC_ATTRIBUTEVALUE: self.srcNodeAttrValue
                                       }
                                   ],
                                    c_serialization.KEY_NODENAME: self.sourceNodeName}]}

    def test_validatorName(self):
        self.assertEqual(self.validator.name, c_testdata.VALIDATOR_NAME,
                         "ValidatorName is not %s" % c_testdata.VALIDATOR_NAME)

    def test_addSourceNode(self):
        self.assertEqual(True, self.validator.addNodeToValidate(self.sourceNode),
                         "Could not .addNodeToValidate?! Name already exists?")

    def test_validatorIterNodes(self):
        self.validator.addNodeToValidate(self.sourceNode)
        nodes = [n for n in self.validator.iterNodes()]

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
