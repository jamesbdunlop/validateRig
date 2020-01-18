#  Copyright (c) 2019.  James Dunlop

import unittest
import logging
import api.vr_core_api as vrigApi
from core import validator as c_validator
from core import nodes as c_nodes
from core import parser as c_parser

logger = logging.getLogger(__name__)


class Test_COREAPI(unittest.TestCase):
    def setUp(self):
        self.validatorName = "testValidator"
        self.sourceNodeName = "testSourceNode"
        self.defaultValueNodeName = "testDefaultValueNode"
        self.connectionNodeName = "testConnectionNode"
        self.jsonPath = "T:\\software\\validateRig\\tests\\testValidator.json"

    def test_createValidatorByName(self):
        validator = vrigApi.createValidator(name=self.validatorName, data=None)
        self.assertIsInstance(validator, c_validator.Validator)
        self.assertEqual(validator.name, self.validatorName)

    def test_createValidatorFromData(self):
        data = c_parser.read(self.jsonPath)
        validator = vrigApi.createValidator(name=self.validatorName, data=data)
        self.assertIsInstance(validator, c_validator.Validator)

    def test_createValidatorNameAsList(self):
        self.assertRaises(
            TypeError,
            vrigApi.createValidator(name=[self.validatorName], data=None),
        )

    def test_createSourceNode(self):
        sourceNode = vrigApi.createSourceNode(
            name=self.sourceNodeName, longName=self.sourceNodeName
        )
        self.assertIsInstance(sourceNode, c_nodes.SourceNode)

    def test_createDefaultValueNode(self):
        defaultValueNode = vrigApi.createDefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
            defaultValue=False,
        )
        self.assertIsInstance(defaultValueNode, c_nodes.DefaultValueNode)

    def test_createConnectionValidityNode(self):
        connectionNode = vrigApi.createConnectionValidityNode(
            name=self.connectionNodeName,
            longName=self.connectionNodeName,
        )
        self.assertIsInstance(connectionNode, c_nodes.ConnectionValidityNode)

    def test_toFile(self):
        validator = vrigApi.createValidator(name=self.validatorName)
        self.assertTrue(
            vrigApi.saveValidatorsToFile(
                validators=[validator], filepath="C:/temp/test.json"
            )
        )


if __name__ == "__main__":  # pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
