from core import validator
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode


def createValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return validator.Validator(name=name)


def createMayaValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return validator.MayaValidator(name=name)


def createSourceNode(name, validityNodes=None):
    """

    :param name: `str`
    :param validityNodes: `list` of either DefaultValueNodes or ConnectionValidityNodes
    :return:
    """
    return SourceNode(name=name, validityNodes=validityNodes)


def createDefaultValueNode(name, value):
    return DefaultValueNode(name=name, value=value)


def createConnectionValidityNode(
    name,
    sourceNodeAttributeName,
    sourceNodeAttributeValue,
    desinationNodeAttributeName,
    destinationNodeAttributeValue,
):
    """

    :param name: `str`
    :param sourceNodeAttributeName: `str`
    :param sourceNodeAttributeValue: `int` | `float` | `bool` | etc
    :param desinationNodeAttributeName: `srt`
    :param destinationNodeAttributeValue: `int` | `float` | `bool` | etc
    :return: `ConnectionValidityNode`
    """
    node = ConnectionValidityNode(name=name)
    node.destAttrName = desinationNodeAttributeName
    node.destAttrValue = destinationNodeAttributeValue
    node.srcAttrName = sourceNodeAttributeName
    node.srcAttrValue = sourceNodeAttributeValue

    return node
