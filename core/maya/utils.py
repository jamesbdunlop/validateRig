#  Copyright (C) Animal Logic Pty Ltd. All rights reserved.
import logging
import maya.cmds as cmds
from maya.api import OpenMaya as om2
from validateRig.core.maya import types as vrcm_types
from validateRig.core.maya import plugs as vrcm_plugs
from validateRig.const import constants as vrconst_constants

logger = logging.getLogger(__name__)


def exists(srcNodeName):
    # type: (str) -> bool

    exists = cmds.objExists(srcNodeName)
    return exists


def cleanMayaLongName(nodeLongName):
    # type: (str) -> str

    newName = nodeLongName.split("|")[-1].split(":")[-1].split(".")[0]

    return newName


def getNamespaceFromLongName(nodeLongName):
    # type: (str) -> str

    nameSpace = ""
    nodeName = nodeLongName.split("|")[-1]
    if ":" in nodeName:
        nameSpace = nodeName.split(":")[0]

    return nameSpace


def getUDAttrs(nodeName):
    lsAttrs = cmds.listAttr(nodeName, ud=True)
    if lsAttrs is None:
        return []

    ud = [ud for ud in cmds.listAttr(nodeName, ud=True) if "_dba" not in ud and ud != "isBeastNode"]
    if ud is None:
        return []

    return ud


def createConnectionData(nodeLongName):
    mSel = om2.MSelectionList()
    mSel.add(nodeLongName)

    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)

    GETATTR_IGNORESTYPES = (vrcm_types.MESSAGE, vrcm_types.MATRIXF44)

    connections = mFn.getConnections()
    sourcePlugs = [plg for plg in connections if plg.isSource]
    logger.debug("%s sourcePlugs:  %s" % (mFn.name(), [plg.name() for plg in sourcePlugs]))
    if not sourcePlugs:
        logger.debug("Skipping!! %s has no sourceplugs!" % mFn.name())
        yield None

    # Find source plugs
    for eachSourcePlug in sourcePlugs:
        logger.debug("Processing sourceMPlug: %s ..." % eachSourcePlug.name())
        srcMPlugType = vrcm_plugs.getMPlugType(eachSourcePlug)
        srcPlugDataDict = dict()

        # [[isElement, isChild, plugName, plgIdx], [isElement, isChild, plugName, plgIdx]]
        plgData = vrcm_plugs.fetchIndexedPlugData(eachSourcePlug)
        logger.debug("%s plgData: %s" % (eachSourcePlug.name(), plgData))
        _, _, srcPlugName, _ = plgData[0]
        if mObj.hasFn(om2.MFn.kDagNode):
            srcPlugDataDict["nodeLongName"] = om2.MDagPath.getAPathTo(mObj).fullPathName()
        else:
            srcPlugDataDict["nodeLongName"] = mFn.absoluteName()

        srcPlugDataDict['attrName'] = srcPlugName
        srcPlugDataDict['plugData'] = plgData
        if srcMPlugType not in GETATTR_IGNORESTYPES:
            value = vrcm_plugs.getMPlugValue(eachSourcePlug)
            logger.debug("attrValue: %s" % value)
            srcPlugDataDict['attrValue'] = value

        # Dest plugs connected to this plug
        # Note .destinations() method skips  over any unit conversion nodes
        destinationPlugs = (mplg for mplg in eachSourcePlug.destinations() if
                            mplg.node().apiType() not in vrconst_constants.MAYA_CONNECTED_NODETYPES_IGNORES)
        if not destinationPlugs:
            logger.debug("%s has no destination connections!" % eachSourcePlug.name())
            continue

        for eachDestMPlug in destinationPlugs:
            logger.debug("Processing destination plug: %s" % eachDestMPlug.name())
            destPlugNodeMFn = om2.MFnDependencyNode(eachDestMPlug.node())

            destPlugData = dict()
            destPlugData["nodeName"] = destPlugNodeMFn.name()
            destMObj = eachDestMPlug.node()
            if destMObj.hasFn(om2.MFn.kDagNode):
                nodeName = om2.MDagPath.getAPathTo(eachDestMPlug.node()).fullPathName()
            else:
                nodeName = destPlugNodeMFn.absoluteName()

            newLongName = "|".join([n for n in nodeName.split("|") if ":" in n])
            destPlugData["nodeLongName"] = newLongName

            destPlugData['plugData'] = vrcm_plugs.fetchIndexedPlugData(eachDestMPlug)

            destPlugType = vrcm_plugs.getMPlugType(eachDestMPlug)
            if destPlugType not in GETATTR_IGNORESTYPES:
                destPlugData['attrValue'] = vrcm_plugs.getMPlugValue(eachDestMPlug)
            logger.debug("destPlugData: %s" % destPlugData)

            connectionData = {"srcData": srcPlugDataDict,
                              "destData": destPlugData}

            destNodeName = destPlugNodeMFn.name().split(":")[-1]
            destLongName = destPlugNodeMFn.absoluteName()

            yield destNodeName, destLongName, connectionData
