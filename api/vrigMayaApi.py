#  Copyright (C) Animal Logic Pty Ltd. All rights reserved.
import logging

from validateRig.api.vrigCoreApi import *
from validateRig.const import constants as vrconst_constants
from validateRig.core.maya import plugs as vrcm_plugs
from validateRig.core.maya import utils as vrcm_utils

logger = logging.getLogger(__name__)
reload(vrcm_utils)
"""
# Example Usage:
# What we're doing in this example...
# Creating a sourceNode for each nurbsCurve's parent transform that ends with "_ctrl"
    # Create a DefaultValueNode for each attribute in ["translate", "rotate", "scale", "rotateOrder"]
    # Createa a DefaultValueNode for userDefined attributes on the curve (if any). 
    # Find connections from this ctrlCrv to any other node for validation. 

from maya.api import OpenMaya as om2
import validateRig.api.vrigMayaApi as vr_maya_api
import validateRig.core.maya.utils as vr_vrcm_utils
#########################################################################################
sourceNodes = list()
crvs = [cmds.listRelatives(crv, p=True, f=True)[0] for crv in cmds.ls(type="nurbsCurve")]
for eachCurve in crvs:
    attributes = ["translate", "rotate", "scale", "rotateOrder"]
    ud = cmds.listAttr(eachCurve, ud=True)
    if ud is not None:
        attributes += ud

    srcNode = vr_maya_api.asSourceNode(nodeLongName=eachCurve, 
                                       attributes=attributes, 
                                       connections=True)
    sourceNodes.append(srcNode)

validator = vr_maya_api.createValidator("testRig")
validator.nameSpace = vr_vrcm_utils.getNamespaceFromLongName(crvs[0])
validator.addSourceNodes(sourceNodes, True)
validator.to_fileJSON(filePath="C:/Temp/testMayaValidator.json")
#########################################################################################
"""


def asSourceNode(nodeLongName, attributes=None, connections=False):
    # type: (str, list[str], bool, bool) -> SourceNode
    logger.debug("###################")
    logger.debug("%s as sourceNode." % nodeLongName)
    validityNodes = list()
    connAttrNames = list()
    if connections:
        logger.debug("connections: %s" % connections)
        connNodes = list(__createConnectionNodes(nodeLongName))
        validityNodes += connNodes
        connAttrNames = [n.connectionData.get("srcData")["attrName"] for n in connNodes]
    logger.debug("validityNodes: %s" % validityNodes)
    logger.debug("connAttrNames: %s" % connAttrNames)
    logger.debug("attributes: %s" % connAttrNames)

    validDefaultValueAttributes = list()
    if attributes is not None:
        for eachAttrName in attributes:
            if eachAttrName not in connAttrNames:
                validDefaultValueAttributes.append(eachAttrName)
    logger.debug("Creating dvNodes for: %s" % validDefaultValueAttributes)

    defaultNodes = list(__createDefaultValueNodes(nodeLongName, validDefaultValueAttributes))
    validityNodes += defaultNodes

    # Now the sourceNodes
    shortName = vrcm_utils.cleanMayaLongName(nodeLongName)
    sourceNode = createSourceNode(name=shortName, longName=nodeLongName, validityNodes=validityNodes)
    logger.debug("shortName: %s" % shortName)
    logger.debug("sourceNode: %s" % sourceNode)
    nameSpace = vrcm_utils.getNamespaceFromLongName(nodeLongName)
    logger.debug("nameSpace: %s" % nameSpace)
    if nameSpace:
        nsShortName = "{}:{}".format(nameSpace, shortName)
        sourceNode.displayName = nsShortName

    return sourceNode


def __createDefaultValueNodes(nodeLongName, defaultAttributes):
    # type: (str, list[str]) -> DefaultValueNode
    for eachAttr in defaultAttributes:
        if eachAttr in vrconst_constants.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES:
            continue

        dvMPlug = vrcm_plugs.getMPlugFromLongName(nodeLongName, eachAttr)
        dvMPlugValue = vrcm_plugs.getMPlugValue(dvMPlug)
        attrData = {eachAttr: dvMPlugValue}

        defaultValueNode = createDefaultValueNode(name=eachAttr, longName=nodeLongName)
        defaultValueNode.defaultValueData = attrData

        yield defaultValueNode


def __createConnectionNodes(nodeLongName):
    # type: (str) -> ConnectionValidityNode

    # We list only the destinations of these attributes.
    for destNodeName, destLongName, connectionData in vrcm_utils.createConnectionData(nodeLongName):
        connectionNode = createConnectionValidityNode(name=destNodeName, longName=destLongName)
        connectionNode.connectionData = connectionData
        logger.debug("ConnectionNode created successfully.")
        logger.debug("destNodeName: %s" % destNodeName)
        logger.debug("destLongName: %s" % destLongName)
        logger.debug("connectionData: ")
        yield connectionNode
