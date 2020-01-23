#  Copyright (c) 2019.  James Dunlop
from core import validator as c_validator
from core import parser as c_parser
from core import factory as c_factory
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode


def createValidator(name, data=None):
    # type: (str, dict) -> c_validator.Validator

    validator = c_factory.createValidator(name=name, data=data)
    return validator


def createSourceNode(name, longName, validityNodes=None):
    # type: (str, str, list[DefaultValueNode, ConnectionValidityNode]) -> None
    """
    :param validityNodes: `list` of either DefaultValueNodes or ConnectionValidityNodes
    """
    node = SourceNode(name=name, longName=longName, validityNodes=validityNodes)
    return node


def createDefaultValueNode(name, longName):
    # type: (str, str, any) -> None
    node = DefaultValueNode(name=name, longName=longName)
    return node


def createConnectionValidityNode(
    name, longName,
):
    # type: (str, str) -> ConnectionValidityNode

    node = ConnectionValidityNode(name=name, longName=longName)

    return node


def saveValidatorsToFile(validators, filepath):
    # type: (list, str) -> bool
    validatorDataList = list()
    for eachValidator in validators:
        validatorDataList.append(eachValidator.toData())

    c_parser.write(filepath=filepath, data=validatorDataList)

    return True
