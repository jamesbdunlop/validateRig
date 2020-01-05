#  Copyright (c) 2019.  James Dunlop
from api import *
from core import inside
from const import constants as c_const
import logging

logger = logging.getLogger(__name__)

if inside.insideMaya():
    from maya import cmds

"""
# Example Usage:
# What we're doing in this example...
# Creating a sourceNode for each nurbsCurve's parent transform that ends with "_ctrl"
    # Create a DefaultValueNode for each attribute in ["translate", "rotate", "scale", "rotateOrder"]
    # Createa a DefaultValueNode for userDefined attributes on the curve (if any). 
        # Note: Attributes listed in const.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES will be skipped as defaultValueNodes are they are not 
        # expected to be set
    # Find connections from this ctrlCrv to any other node for validation. 

import api_maya as vr_mayaApi
import const.constants as c_const
import core.validator as cval

sourceNodes = list()
crvs = [cmds.listRelatives(crv, p=True, f=True)[0] for crv in cmds.ls(type="nurbsCurve")]
for eachCurve in crvs:
    attributes= ["translate", "rotate", "scale", "rotateOrder"]
    ud = cmds.listAttr(eachCurve, ud=True)
    if ud is not None:
        attributes += ud
    
    srcNode = vr_mayaApi.asSourceNode(nodeLongName=eachCurve, 
                                      attributes=attributes, 
                                      connections=True)
    sourceNodes.append(srcNode)

validator = vr_mayaApi.createValidator("myTestChar")
validator.nameSpace = "testRigNamespace"
validator.addSourceNodes(sourceNodes, True)
validator.to_fileJSON(filePath="C:/temp/testValidator.json")

"""


def asSourceNode(nodeLongName, attributes=None, connections=False):
    # type: (str, list[str], bool, bool) -> SourceNode

    validityNodes = list()

    if attributes is not None:
        validityNodes += list(__createDefaultValueNodes(nodeLongName, attributes))

    if connections:
        validityNodes += list(__createConnectionNodes(nodeLongName))

    # Now the sourceNodes
    shortName = cleanMayaLongName(nodeLongName)
    nameSpace = getNamespaceFromLongName(nodeLongName)
    nsShortName = shortName
    if nameSpace:
        nsShortName = "{}:{}".format(nameSpace, shortName)

    sourceNode = createSourceNode(
        name=shortName, longName=nodeLongName, validityNodes=validityNodes
    )
    sourceNode.displayName = nsShortName

    return sourceNode


def __createDefaultValueNodes(nodeLongName, defaultAttributes):
    # type: (str, list[str]) -> DefaultValueNode
    for eachAttr in defaultAttributes:
        if eachAttr in c_const.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES:
            continue

        attrName, attrValue = getAttrValue(nodeLongName, eachAttr)
        defaultValueNode = createDefaultValueNode(
            name=eachAttr, longName=attrName, defaultValue=attrValue
        )

        yield defaultValueNode


def __createConnectionNodes(nodeLongName):
    # type: (str) -> ConnectionValidityNode

    # We list only the destinations of these attributes.
    conns = cmds.listConnections(
        nodeLongName,
        connections=True,
        source=False,
        destination=True,
        plugs=True,
        skipConversionNodes=True,
    )

    if conns is not None:
        for x in range(0, len(conns), 2):
            src = conns[x]
            dest = conns[x + 1]

            srcFullAttributeName = ".".join(src.split(".")[1:])
            srcShortAttributeName = src.split(".")[-1]

            if cmds.nodeType(dest) in c_const.MAYA_CONNECTED_NODETYPES_IGNORES:
                continue

            destFullAttributeName = ".".join(dest.split(".")[1:])
            destShortAttributeName = dest.split(".")[-1]

            if not srcShortAttributeName in c_const.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES:
                sourceNodeAttributeValue = cmds.getAttr(src)
            else:
                sourceNodeAttributeValue = None

            if not destShortAttributeName in c_const.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES:
                destinationNodeAttributeValue = cmds.getAttr(dest)
            else:
                destinationNodeAttributeValue = None

            destShortNodeName = cleanMayaLongName(dest)
            destLongName = cmds.ls(dest, l=True)[0]
            connectionNode = createConnectionValidityNode(
                name=destShortNodeName,
                longName=destLongName,
                sourceNodeAttributeName=srcFullAttributeName,
                sourceNodeAttributeValue=sourceNodeAttributeValue,
                desinationNodeAttributeName=destFullAttributeName,
                destinationNodeAttributeValue=destinationNodeAttributeValue,
            )

            nameSpace = getNamespaceFromLongName(destLongName)
            nsShortName = destShortNodeName
            if nameSpace:
                nsShortName = "{}:{}".format(nameSpace, destShortNodeName)

            connectionNode.displayName = nsShortName

            yield connectionNode


####################################################################################################
# UTILS
def cleanMayaLongName(nodeLongName):
    # type: (str) -> str
    newName = nodeLongName.split("|")[-1].split(":")[-1].split(".")[0]

    return newName


def getAttrValue(nodeLongName, attributeName):
    # type: (str, str) -> any
    attrName = "{}.{}".format(nodeLongName, attributeName)
    value = cmds.getAttr(attrName)
    if isinstance(value, list):
        value = value[0]

    return attrName, value


def getNamespaceFromLongName(nodeLongName):
    nameSpace = ""
    if ":" in nodeLongName:
        nameSpace = nodeLongName.split("|")[-1].split(":")[0]

    return nameSpace