#  Copyright (c) 2019.  James Dunlop
import logging

from maya.api import OpenMaya as om2

from api import *

from const import constants as c_const

from core.maya import types as cm_types
from core.maya import plugs as cm_plugs
from core.maya import utils as cm_utils

logger = logging.getLogger(__name__)

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
    shortName = cm_utils.cleanMayaLongName(nodeLongName)
    nameSpace = cm_utils.getNamespaceFromLongName(nodeLongName)
    nsShortName = shortName
    if nameSpace:
        nsShortName = "{}:{}".format(nameSpace, shortName)

    sourceNode = createSourceNode(name=shortName,
                                  longName=nodeLongName,
                                  validityNodes=validityNodes)
    sourceNode.displayName = nsShortName

    return sourceNode


def __createDefaultValueNodes(nodeLongName, defaultAttributes):
    # type: (str, list[str]) -> DefaultValueNode
    for eachAttr in defaultAttributes:
        if eachAttr in c_const.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES:
            continue

        longAttrName = "{}.{}".format(nodeLongName, eachAttr)
        attrValue = cm_utils.getAttrValue(nodeLongName, eachAttr)
        defaultValueNode = createDefaultValueNode(name=eachAttr,
                                                  longName=longAttrName,
                                                  defaultValue=attrValue)

        yield defaultValueNode


def __createConnectionNodes(nodeLongName):
    # type: (str) -> ConnectionValidityNode

    # We list only the destinations of these attributes.
    mSel = om2.MSelectionList()
    mSel.add(nodeLongName)
    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)
    conns = mFn.getConnections()
    if not conns:
        yield []

    for eachPlug in conns:
        if not eachPlug.isSource:
            continue
        srcPlugName = eachPlug.name()
        srcFullAttributeName = ".".join(srcPlugName.split(".")[1:])
        srcPlugType = cm_plugs.getPlugType(eachPlug)
        sourceNodeAttributeValue = None
        if srcPlugType not in (cm_types.MESSAGE, cm_types.MATRIXF44):
            sourceNodeAttributeValue = cm_plugs.getPlugValue(eachPlug)

        destinations = eachPlug.destinations()
        for eachDestPlug in destinations:
            destShortNodeName, destLongName, destFullAttributeName, destinationAttributeValue = processDestinationPlug(eachDestPlug)

            connectionNode = createConnectionValidityNode(
                name=destShortNodeName,
                longName=destLongName,
                sourceNodeAttributeName=srcFullAttributeName,
                sourceNodeAttributeValue=sourceNodeAttributeValue,
                desinationNodeAttributeName=destFullAttributeName,
                destinationNodeAttributeValue=destinationAttributeValue,
            )

            nameSpace = cm_utils.getNamespaceFromLongName(destLongName)
            nsShortName = destShortNodeName
            if nameSpace:
                nsShortName = "{}:{}".format(nameSpace, destShortNodeName)

            connectionNode.displayName = nsShortName

            yield connectionNode


def processDestinationPlug(mPlug):
    # type: (om2.MPlug) -> list[str, str, str, str]

    destPlugName = mPlug.name()
    destPlugType = cm_plugs.getPlugType(mPlug)
    destWithoutAttrName = destPlugName.split(".")[0]
    destFullAttributeName = ".".join(destPlugName.split(".")[1:])

    destinationAttributeValue = None
    if destPlugType not in (cm_types.MESSAGE, cm_types.MATRIXF44):
        destinationAttributeValue = cm_plugs.getPlugValue(mPlug)

    # proper fullPathName
    destShortNodeName = cm_utils.cleanMayaLongName(destPlugName)
    mSel = om2.MSelectionList()
    mSel.add(destWithoutAttrName)
    if mSel.getDependNode(0).hasFn(om2.MFn.kDagNode):
        destFullPathName = om2.MDagPath.getAPathTo(mSel.getDependNode(0)).partialPathName()
        destLongName = destFullPathName
    else:
        destLongName = destWithoutAttrName

    return destShortNodeName, destLongName, destFullAttributeName, destinationAttributeValue
