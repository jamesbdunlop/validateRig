#  Copyright (c) 2019.  James Dunlop
import logging

from api.vr_core_api import *

from maya.api import OpenMaya as om2

from const import constants as c_const

from core.maya import types as cm_types
from core.maya import plugs as cm_plugs
from core.maya import utils as cm_utils
reload(cm_utils)
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
    if connections:
        validityNodes += list(__createConnectionNodes(nodeLongName))

    if attributes is not None:
        validityNodes += list(__createDefaultValueNodes(nodeLongName, attributes))

    # Now the sourceNodes
    shortName = cm_utils.cleanMayaLongName(nodeLongName)
    sourceNode = createSourceNode(name=shortName,
                                  longName=nodeLongName,
                                  validityNodes=validityNodes)

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
    GETATTR_IGNORESTYPES = (cm_types.MESSAGE, cm_types.MATRIXF44)
    if conns:
        # Find source plugs
        for eachConnMPlug in conns:
            if not eachConnMPlug.isSource:
                continue

            srcMPlugAttrName = eachConnMPlug.partialName(False, False, False, True, True, True)
            srcMPlugType = cm_plugs.getMPlugType(eachConnMPlug)

            srcMPlugAttrValue = None
            if srcMPlugType not in GETATTR_IGNORESTYPES:
                srcMPlugAttrValue = cm_plugs.getMPlugValue(eachConnMPlug)

            srcIsElement, srcIsChild, srcAttrIndex, srcAttrName = _fetchIndexedPlugData(eachConnMPlug)
            if srcIsChild:
                srcMPlugAttrName = srcAttrName

            # Dest plugs connected to this plug
            destinations = eachConnMPlug.destinations() # method skips over any unit conversion nodes
            for eachDestMPlug in destinations:
                destPlugNodeMFn = om2.MFnDependencyNode(eachDestMPlug.node())

                # Skip entirely shitty maya nodes we don't care about
                if eachDestMPlug.node().apiType() in (om2.MFn.kMessageAttribute,
                                                      om2.MFn.kNodeGraphEditorBookmarks,
                                                      om2.MFn.kNodeGraphEditorBookmarkInfo,
                                                      om2.MFn.kNodeGraphEditorInfo,
                                                      om2.MFn.kContainer,
                                                      ):
                    continue

                destMPlugAttrName = str(eachDestMPlug.partialName(False, False, False, True, True, True))
                destPlugType = cm_plugs.getMPlugType(eachDestMPlug)

                destinationAttributeValue = None
                if destPlugType not in GETATTR_IGNORESTYPES:
                    destinationAttributeValue = cm_plugs.getMPlugValue(eachDestMPlug)

                destIsElement, destIsChild, destAttrIndex, destAttrName = _fetchIndexedPlugData(eachDestMPlug)
                if destIsChild:
                    destMPlugAttrName = destAttrName

                #################
                # Create Node now
                connectionNode = createConnectionValidityNode(
                    name=destPlugNodeMFn.name(),
                    longName=destPlugNodeMFn.absoluteName(),
                )
                connectionNode.srcAttrName = srcMPlugAttrName
                connectionNode.srcAttrValue = srcMPlugAttrValue
                connectionNode.srcAttrIsIndexed = any((srcIsElement, srcIsChild))
                connectionNode.srcAttrIndex = srcAttrIndex

                connectionNode.destAttrName = destMPlugAttrName
                connectionNode.destAttrValue = destinationAttributeValue
                connectionNode.destAttrIsIndexed = any((destIsElement, destIsChild))
                connectionNode.destAttrIndex = destAttrIndex

                yield connectionNode


def _fetchIndexedPlugData(mplug):
    isIndexedMPlug = cm_plugs.isMPlugIndexed(mplug)
    attrIndex = None
    attrName = None
    if isIndexedMPlug and mplug.isElement:
        attrIndex = mplug.logicalIndex()
        print(mplug.name())
        print(attrIndex)

    elif mplug.isChild:
        parent = mplug.parent()
        attrName = parent.partialName(False, False, False, True, True, True)
        for x in range(parent.numChildren()):
            if parent.child(x) == mplug:
                attrIndex = x

    return [mplug.isElement, mplug.isChild, attrIndex, attrName]
