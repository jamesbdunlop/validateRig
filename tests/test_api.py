import unittest
import logging
import api as validationAPI
from core import validator as c_validator
from core import nodes as c_nodes

logger = logging.getLogger(__name__)


class Test_Validator(unittest.TestCase):
    def setUp(self):
        self.validatorName = "testValidator"
        self.sourceNodeName = "testSourceNode"
        self.defaultValueNodeName = "testDefaultValueNode"
        self.connectionNodeName = "testConnectionNode"

    def test_createValidator(self):
        validator = validationAPI.createValidator(name=self.validatorName)
        self.assertIsInstance(validator, c_validator.Validator)

    def test_createMayaValidator(self):
        validator = validationAPI.createMayaValidator(name=self.validatorName)
        self.assertIsInstance(validator, c_validator.MayaValidator)

    def test_createSourceNode(self):
        sourceNode = validationAPI.createSourceNode(name=self.sourceNodeName,
                                                    longName=self.sourceNodeName)
        self.assertIsInstance(sourceNode, c_nodes.SourceNode)

    def test_createDefaultValueNode(self):
        defaultValueNode = validationAPI.createDefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
            defaultValue=False
        )
        self.assertIsInstance(defaultValueNode, c_nodes.DefaultValueNode)

    def test_createConnectionValidityNode(self):
        connectionNode = validationAPI.createConnectionValidityNode(
            name=self.connectionNodeName,
            longName=self.connectionNodeName,
            sourceNodeAttributeName="test",
            sourceNodeAttributeValue=0,
            desinationNodeAttributeName="test",
            destinationNodeAttributeValue=0,
        )
        self.assertIsInstance(connectionNode, c_nodes.ConnectionValidityNode)


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
