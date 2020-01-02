#  Copyright (c) 2019.  James Dunlop

import unittest
import logging
import api as validationAPI
from core import validator as c_validator
from core import nodes as c_nodes
from core import parser as c_parser

logger = logging.getLogger(__name__)


class Test_Validator(unittest.TestCase):
    def setUp(self):
        self.validatorName = "testValidator"
        self.sourceNodeName = "testSourceNode"
        self.defaultValueNodeName = "testDefaultValueNode"
        self.connectionNodeName = "testConnectionNode"
        self.jsonPath = "T:\\software\\validateRig\\tests\\testValidator.json"

    def test_createValidatorByName(self):
        validator = validationAPI.createValidator(name=self.validatorName, data=None)
        self.assertIsInstance(validator, c_validator.Validator)
        self.assertEqual(validator.name, self.validatorName)

    def test_createValidatorFromData(self):
        data = c_parser.read(self.jsonPath)
        validator = validationAPI.createValidator(name=self.validatorName, data=data)
        self.assertIsInstance(validator, c_validator.Validator)

    def test_createValidatorNameAsList(self):
        self.assertRaises(
            TypeError,
            validationAPI.createValidator(name=[self.validatorName], data=None),
        )

    def test_createSourceNode(self):
        sourceNode = validationAPI.createSourceNode(
            name=self.sourceNodeName, longName=self.sourceNodeName
        )
        self.assertIsInstance(sourceNode, c_nodes.SourceNode)

    def test_createDefaultValueNode(self):
        defaultValueNode = validationAPI.createDefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
            defaultValue=False,
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

    def test_toFile(self):
        validator = validationAPI.createValidator(name=self.validatorName)
        self.assertTrue(
            validationAPI.saveValidatorsToFile(
                validators=[validator], filepath="C:/temp/test.json"
            )
        )


if __name__ == "__main__":  # pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
