#  Copyright (c) 2019.  James Dunlop

from core import validator as c_validator
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode

"""
# Very quick usage example in maya
import api as vrAPI

validator = vrAPI.createValidator("test")
sourceNodes = list()
for e in cmds.ls(sl=True, l=True):
    # Default Values
    # Regular Attributes
    attrs = ("translate", "rotate", "scale")
    validityNodes = list()
    srtNodes = [vrAPI.createDefaultValueNode(name=attr, longName=attr, defaultValue=cmds.getAttr("{}.{}".format(e, attr))[0]) for attr in attrs]
    validityNodes += srtNodes


    # Connections
    connectedAttributes =list()    
    conns = cmds.listConnections(e, c=True, source=False, destination=True, plugs=True)
    connNodes = list()
    if conns is not None:
        for x in range(0, len(conns), 2):
            src = conns[x]
            dest = conns[x+1]
            srcAttributeName = src.split(".")[-1]
            if srcAttributeName == "message":
                continue
                
            connectionNode = vrAPI.createConnectionValidityNode(name=dest.split(".")[0],longName=dest,
                                                                sourceNodeAttributeName = srcAttributeName,
                                                                sourceNodeAttributeValue = cmds.getAttr(src),
                                                                desinationNodeAttributeName = dest.split(".")[-1],
                                                                destinationNodeAttributeValue = cmds.getAttr(dest))

            connNodes.append(connectionNode)
            connectedAttributes.append(srcAttributeName)
            
    validityNodes += connNodes
    
    # User Defined attributes. Do these now to check against anything that might be connected AND is a UDefined. Smelly but meh.
    if cmds.listAttr(e, ud=True):
        UDAttributes = [vrAPI.createDefaultValueNode(name=attr, longName=attr, defaultValue=cmds.getAttr("{}.{}".format(e, attr))) for attr in cmds.listAttr(e, ud=True)]
        for eachAttr in UDAttributes:
            if eachAttr.name in connectedAttributes:
                UDAttributes.remove(eachAttr) 
        
        validityNodes += UDAttributes
    
    sourceNode = vrAPI.createSourceNode(name=e.split("|")[-1], longName=e, validityNodes=validityNodes)
    validator.addSourceNode(sourceNode)

# This file can then be loaded into the UI
validator.to_fileJSON(filePath="C:/temp/testValidator.json")
"""


def createValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return c_validator.Validator(name=name)


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
    node.srcAttrName = sourceNodeAttributeName
    node.srcAttrValue = sourceNodeAttributeValue
    node.destAttrName = desinationNodeAttributeName
    node.destAttrValue = destinationNodeAttributeValue

    return node
