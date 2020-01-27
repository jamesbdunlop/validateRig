#  Copyright (c) 2019.  James Dunlop

import unittest
import logging

from validateRig.api import vrigCoreApi as vrapi_core
from validateRig.core import validator as vrc_validator
from validateRig.core import nodes as vrc_nodes
from validateRig.core import parser as vrc_parser

logger = logging.getLogger(__name__)


class Test_COREAPI(unittest.TestCase):
    def setUp(self):
        self.validatorName = "testValidator"
        self.sourceNodeName = "testSourceNode"
        self.defaultValueNodeName = "testDefaultValueNode"
        self.connectionNodeName = "testConnectionNode"
        self.jsonPath = "T:\\software\\validateRig\\tests\\testValidator.json"

    def test_createValidatorByName(self):
        validator = vrapi_core.createValidator(name=self.validatorName, data=None)
        self.assertIsInstance(validator, vrc_validator.Validator)
        self.assertEqual(validator.name, self.validatorName)

    def test_createValidatorFromData(self):
        data = vrc_parser.read(self.jsonPath)
        validator = vrapi_core.createValidator(name=self.validatorName, data=data)
        self.assertIsInstance(validator, vrc_validator.Validator)

    def test_createValidatorNameAsList(self):
        self.assertRaises(
            TypeError,
            vrapi_core.createValidator(name=[self.validatorName], data=None),
        )

    def test_createSourceNode(self):
        sourceNode = vrapi_core.createSourceNode(
            name=self.sourceNodeName, longName=self.sourceNodeName
        )
        self.assertIsInstance(sourceNode, vrc_nodes.SourceNode)

    def test_createDefaultValueNode(self):
        defaultValueNode = vrapi_core.createDefaultValueNode(
            name=self.defaultValueNodeName,
            longName=self.defaultValueNodeName,
        )
        self.assertIsInstance(defaultValueNode, vrc_nodes.DefaultValueNode)

    def test_createConnectionValidityNode(self):
        connectionNode = vrapi_core.createConnectionValidityNode(
            name=self.connectionNodeName,
            longName=self.connectionNodeName,
        )
        self.assertIsInstance(connectionNode, vrc_nodes.ConnectionValidityNode)

    def test_toFile(self):
        validator = vrapi_core.createValidator(name=self.validatorName)
        self.assertTrue(
            vrapi_core.saveValidatorsToFile(
                validators=[validator], filepath="C:/temp/test.json"
            )
        )


if __name__ == "__main__":  # pragma: no cover
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite())
