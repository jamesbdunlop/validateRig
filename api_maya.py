#  Copyright (c) 2019.  James Dunlop
import logging
from api import *
from const import constants as c_const
from core.maya import types as cm_types
from core.maya import plugs as cm_plugs
reload(cm_plugs)
logger = logging.getLogger(__name__)

from maya.api import OpenMaya as om2

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
        print(srcPlugType)
        sourceNodeAttributeValue = None
        if srcPlugType not in (cm_types.MESSAGE, cm_types.MATRIXF44):
            sourceNodeAttributeValue = cm_plugs.getPlugValue(eachPlug)

        destinations = eachPlug.destinations()
        for eachDestPlug in destinations:
            destPlugName = eachDestPlug.name()
            destPlugType = cm_plugs.getPlugType(eachDestPlug)
            destWithoutAttrName = destPlugName.split(".")[0]
            destFullAttributeName = ".".join(destPlugName.split(".")[1:])

            destinationNodeAttributeValue = None
            if destPlugType not in (cm_types.MESSAGE, cm_types.MATRIXF44):
                destinationNodeAttributeValue = cm_plugs.getPlugValue(eachDestPlug)

            # proper fullPathName
            destShortNodeName = cleanMayaLongName(destPlugName)
            mSel = om2.MSelectionList()
            mSel.add(destWithoutAttrName)
            if mSel.getDependNode(0).hasFn(om2.MFn.kDagNode):
                destFullPathName = om2.MDagPath.getAPathTo(mSel.getDependNode(0)).partialPathName()
                destLongName = destFullPathName
            else:
                destLongName = destWithoutAttrName

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

    fullAttrName = "{}.{}".format(nodeLongName, attributeName)
    mSel = om2.MSelectionList()
    mSel.add(nodeLongName)
    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)
    plg = mFn.findPlug(attributeName, False)

    ignoreTypes = (cm_types.MESSAGE, )
    plugType = cm_plugs.getPlugType(plg)

    if plugType in ignoreTypes:
        return None

    value = cm_plugs.getPlugValue(plg)

    return fullAttrName, value


def getNamespaceFromLongName(nodeLongName):
    nameSpace = ""
    if ":" in nodeLongName:
        nameSpace = nodeLongName.split("|")[-1].split(":")[0]

    return nameSpace
