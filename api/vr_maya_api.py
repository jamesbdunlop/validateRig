#  Copyright (c) 2019.  James Dunlop
import logging

from api.vr_core_api import *

from maya.api import OpenMaya as om2

from const import constants as c_const

from core.maya import types as cm_types
from core.maya import plugs as cm_plugs
from core.maya import utils as cm_utils
reload(cm_plugs)
logger = logging.getLogger(__name__)

"""
# Example Usage:
# What we're doing in this example...
# Creating a sourceNode for each nurbsCurve's parent transform that ends with "_ctrl"
    # Create a DefaultValueNode for each attribute in ["translate", "rotate", "scale", "rotateOrder"]
    # Createa a DefaultValueNode for userDefined attributes on the curve (if any). 
    # Find connections from this ctrlCrv to any other node for validation. 

from maya.api import OpenMaya as om2
import validateRig.api.vr_maya_api as vr_maya_api
import validateRig.core.maya.utils as vr_cm_utils
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
validator.nameSpace = vr_cm_utils.getNamespaceFromLongName(crvs[0])
validator.addSourceNodes(sourceNodes, True)
validator.to_fileJSON(filePath="C:/Temp/testMayaValidator.json")
#########################################################################################
"""


def asSourceNode(nodeLongName, attributes=None, connections=False):
    # type: (str, list[str], bool, bool) -> SourceNode

    validityNodes = list()
    # connAttrNames = list()
    if connections:
        connNodes = list(__createConnectionNodes(nodeLongName))
        validityNodes += connNodes
        # connAttrNames = [n.srcAttrName for n in connNodes]

    if attributes is not None:
        defaultNodes = list(__createDefaultValueNodes(nodeLongName, attributes))
        # for eachDefaultNode in defaultNodes:
            # if eachDefaultNode.name in connAttrNames:
            #     defaultNodes.remove(eachDefaultNode)
        validityNodes += defaultNodes

    # Now the sourceNodes
    shortName = cm_utils.cleanMayaLongName(nodeLongName)
    sourceNode = createSourceNode(
        name=shortName, longName=nodeLongName, validityNodes=validityNodes
    )

    nameSpace = cm_utils.getNamespaceFromLongName(nodeLongName)
    if nameSpace:
        nsShortName = "{}:{}".format(nameSpace, shortName)
        sourceNode.displayName = nsShortName

    return sourceNode


def __createDefaultValueNodes(nodeLongName, defaultAttributes):
    # type: (str, list[str]) -> DefaultValueNode
    for eachAttr in defaultAttributes:
        if eachAttr in c_const.MAYA_DEFAULTVALUEATTRIBUTE_IGNORES:
            continue

        attrValue = cm_utils.getAttrValue(nodeLongName, eachAttr)
        attrData = {eachAttr: attrValue}

        defaultValueNode = createDefaultValueNode(name=eachAttr, longName=nodeLongName)
        defaultValueNode.defaultValueData = attrData

        yield defaultValueNode


def __createConnectionNodes(nodeLongName):
    # type: (str) -> ConnectionValidityNode

    # We list only the destinations of these attributes.
    mSel = om2.MSelectionList()
    mSel.add(nodeLongName)
    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)

    conns = mFn.getConnections()
    GETATTR_IGNORESTYPES = (cm_types.MESSAGE, cm_types.MATRIXF44)
    if conns:
        # Find source plugs
        for eachConnMPlug in conns:
            if not eachConnMPlug.isSource:
                continue

            srcMPlugType = cm_plugs.getMPlugType(eachConnMPlug)
            srcPlugDataDict = dict()

            #[[isElement, isChild, plugName, plgIdx], [isElement, isChild, plugName, plgIdx]]
            plgData = cm_plugs.fetchIndexedPlugData(eachConnMPlug)
            _, _, srcPlugName, _ = plgData[0]
            srcPlugDataDict['attrName'] = srcPlugName
            srcPlugDataDict['plugData'] = plgData
            if srcMPlugType not in GETATTR_IGNORESTYPES:
                srcPlugDataDict['attrValue'] = cm_plugs.getMPlugValue(eachConnMPlug)

            # Dest plugs connected to this plug
            destinations = (eachConnMPlug.destinations())  # method skips over any unit conversion nodes
            for eachDestMPlug in destinations:
                destPlugNodeMFn = om2.MFnDependencyNode(eachDestMPlug.node())

                # Skip entirely shitty maya nodes we don't care about
                if eachDestMPlug.node().apiType() in c_const.MAYA_CONNECTED_NODETYPES_IGNORES:
                    continue

                destPlugType = cm_plugs.getMPlugType(eachDestMPlug)
                destPlugDataDict = dict()
                destPlugDataDict["nodeName"] = om2.MFnDependencyNode(eachDestMPlug.node()).name()
                destPlugDataDict['plugData'] = cm_plugs.fetchIndexedPlugData(eachDestMPlug)
                if destPlugType not in GETATTR_IGNORESTYPES:
                    destPlugDataDict['attrValue'] = cm_plugs.getMPlugValue(eachDestMPlug)

                #################
                # Create Node now
                connectionNode = createConnectionValidityNode(name=mFn.name(),
                                                              longName=nodeLongName
                                                              )
                connectionNode.connectionData = {"srcData": srcPlugDataDict,
                                                 "destData": destPlugDataDict}
                yield connectionNode
