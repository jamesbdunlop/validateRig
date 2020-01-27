#  Copyright (c) 2019.  James Dunlop
import logging

from validateRig.api.vrigCoreApi import *
from validateRig.const import constants as c_const
from validateRig.core.maya import types as cm_types
from validateRig.core.maya import plugs as cm_plugs
from validateRig.core.maya import utils as cm_utils

from maya.api import OpenMaya as om2

logger = logging.getLogger(__name__)

reload(cm_plugs)
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
    connAttrNames = list()
    if connections:
        connNodes = list(__createConnectionNodes(nodeLongName))
        validityNodes += connNodes
        connAttrNames = [set(n.connectionData.get("srcData")["attrName"] for n in connNodes)]
    logger.debug("connAttrNames: %s" % connAttrNames)

    if attributes is not None:
        defaultNodes = list(__createDefaultValueNodes(nodeLongName, attributes))
        for eachDefaultNode in defaultNodes:
            data = eachDefaultNode.defaultValueData
            for dvName, _ in data.iteritems():
                if dvName in connAttrNames:
                    defaultNodes.remove(eachDefaultNode)

        validityNodes += defaultNodes

    # Now the sourceNodes
    shortName = cm_utils.cleanMayaLongName(nodeLongName)
    sourceNode = createSourceNode(name=shortName, longName=nodeLongName, validityNodes=validityNodes)

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

    GETATTR_IGNORESTYPES = (cm_types.MESSAGE, cm_types.MATRIXF44)

    connections = mFn.getConnections()
    sourcePlugs = [plg for plg in connections if plg.isSource]
    logger.debug("%s sourcePlugs:  %s" % (mFn.name(), [plg.name() for plg in sourcePlugs]))
    if not sourcePlugs:
        logger.debug("Skipping!! %s has no sourceplugs!" % mFn.name())
        yield None

    # Find source plugs
    for eachSourcePlug in sourcePlugs:
        logger.debug("Processing sourceMPlug: %s ..." % eachSourcePlug.name())
        srcMPlugType = cm_plugs.getMPlugType(eachSourcePlug)
        srcPlugDataDict = dict()

        # [[isElement, isChild, plugName, plgIdx], [isElement, isChild, plugName, plgIdx]]
        plgData = cm_plugs.fetchIndexedPlugData(eachSourcePlug)
        logger.debug("%s plgData: %s" % (eachSourcePlug.name(), plgData))
        _, _, srcPlugName, _ = plgData[0]
        srcPlugDataDict['attrName'] = srcPlugName
        srcPlugDataDict['plugData'] = plgData
        if srcMPlugType not in GETATTR_IGNORESTYPES:
            value = cm_plugs.getMPlugValue(eachSourcePlug)
            logger.debug("attrValue: %s" % value)
            srcPlugDataDict['attrValue'] = value

        # Dest plugs connected to this plug
        # Note .destinations() method skips  over any unit conversion nodes
        destinationPlugs = (mplg for mplg in eachSourcePlug.destinations() if
                            mplg.node().apiType() not in c_const.MAYA_CONNECTED_NODETYPES_IGNORES)
        if not destinationPlugs:
            logger.debug("%s has no destination connections!" % eachSourcePlug.name())
            continue

        for eachDestMPlug in destinationPlugs:
            logger.debug("Processing destination plug: %s" % eachDestMPlug.name())
            destPlugData = dict()
            destPlugData["nodeName"] = om2.MFnDependencyNode(eachDestMPlug.node()).name()
            # validateRig.api.vrigMayaApi : Processing destination plug: testRigNamespace:jd_hermiteArrayCrv1.cvs[0].worldMtx
            # core.maya.plugs : mPlug: testRigNamespace:jd_hermiteArrayCrv1.cvs[0].worldMtx isIndexed: True #
            # core.maya.plugs : Cleaning partialName: cvs[0] #
            # core.maya.plugs : PLUGDATA: [[False, True, u'cvs', 2]]  #
            destPlugData['plugData'] = cm_plugs.fetchIndexedPlugData(eachDestMPlug)

            destPlugType = cm_plugs.getMPlugType(eachDestMPlug)
            if destPlugType not in GETATTR_IGNORESTYPES:
                destPlugData['attrValue'] = cm_plugs.getMPlugValue(eachDestMPlug)
            logger.debug("destPlugData: %s" % destPlugData)

            #################
            # Create Node now
            destPlugNodeMFn = om2.MFnDependencyNode(eachDestMPlug.node())
            connectionNode = createConnectionValidityNode(name=destPlugNodeMFn.name().split(":")[-1],
                                                          longName=destPlugNodeMFn.absoluteName()
                                                          )
            connectionNode.connectionData = {"srcData": srcPlugDataDict,
                                             "destData": destPlugData}
            logger.debug("ConnectionNode created successfully.")
            logger.debug("####################################")
            yield connectionNode
