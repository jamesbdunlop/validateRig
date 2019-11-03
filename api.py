from core import validator as c_validator
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode

"""
# Very quick usage example in maya
import api as vrAPI

validator = vrAPI.createValidator("test")
sourceNodes = list()
for e in cmds.ls(sl=True):
    attrs = ("translate", "rotate", "scale")
    sourceNodes = list()
    srtNodes = [vrAPI.createDefaultValueNode(name=attr, defaultValue=cmds.getAttr("{}.{}".format(e, attr))) for attr in attrs]
    sourceNodes += srtNodes
    
    if cmds.listAttr(e, ud=True):
        udefinedAttributes = [vrAPI.createDefaultValueNode(name=attr, defaultValue=cmds.getAttr("{}.{}".format(e, attr))) for attr in cmds.listAttr(e, ud=True)]
        sourceNodes += udefinedAttributes
    
    sourceNode = vrAPI.createSourceNode(name=e.split("|")[-1], longName=e, validityNodes=sourceNodes)
    validator.addSourceNode(sourceNode)
    
validator.to_fileJSON(filePath="C:/temp/testValidator.json")
# This file can then be loaded into the UI
"""

def createValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return c_validator.Validator(name=name)


def createMayaValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return c_validator.MayaValidator(name=name)


def createSourceNode(name, longName, validityNodes=None):
    """

    :param name: `str`
    :param longName: `str`
    :param validityNodes: `list` of either DefaultValueNodes or ConnectionValidityNodes
    :return:
    """
    return SourceNode(name=name, longName=longName, validityNodes=validityNodes)


def createDefaultValueNode(name, longName, defaultValue):
    """

    :param name: `str`
    :param longName: `str`
    :param defaultValue: `int` | `float` | `bool` | etc
    :return:
    """
    return DefaultValueNode(name=name, longName=longName, defaultValue=defaultValue)


def createConnectionValidityNode(
    name,
    longName,
    sourceNodeAttributeName,
    sourceNodeAttributeValue,
    desinationNodeAttributeName,
    destinationNodeAttributeValue,
):
    """

    :param name: `str`
    :param longName: `str`
    :param sourceNodeAttributeName: `str`
    :param sourceNodeAttributeValue: `int` | `float` | `bool` | etc
    :param desinationNodeAttributeName: `srt`
    :param destinationNodeAttributeValue: `int` | `float` | `bool` | etc
    :return: `ConnectionValidityNode`
    """
    node = ConnectionValidityNode(name=name, longName=longName)
    node.destAttrName = desinationNodeAttributeName
    node.destAttrValue = destinationNodeAttributeValue
    node.srcAttrName = sourceNodeAttributeName
    node.srcAttrValue = sourceNodeAttributeValue

    return node

