#  Copyright (c) 2020.  James Dunlop
import logging
import maya.cmds as cmds
from maya.api import OpenMaya as om2
from core.maya import types as cm_types
from core.maya import plugs as cm_plugs

logger = logging.getLogger(__name__)


def exists(srcNodeName):
    # type: (str) -> bool

    exists = cmds.objExists(srcNodeName)
    if not exists:
        logger.error("Failed to find sourceNode %s in scene!" % srcNodeName)

    return exists


def cleanMayaLongName(nodeLongName):
    # type: (str) -> str

    newName = nodeLongName.split("|")[-1].split(":")[-1].split(".")[0]

    return newName


def getAttrValue(nodeLongName, attributeName):
    # type: (str, str) -> list[str, any]

    mSel = om2.MSelectionList()
    mSel.add(nodeLongName)
    mObj = mSel.getDependNode(0)
    mFn = om2.MFnDependencyNode(mObj)
    plg = mFn.findPlug(attributeName, False)

    ignoreTypes = (cm_types.MESSAGE,)  # can't query for and I don't care to.
    plugType = cm_plugs.getMPlugType(plg)

    if plugType in ignoreTypes:
        return None

    value = cm_plugs.getMPlugValue(plg)

    return value


def getNamespaceFromLongName(nodeLongName):
    # type: (str) -> str

    nameSpace = ""
    nodeName = nodeLongName.split("|")[-1]
    if ":" in nodeName:
        nameSpace = nodeName.split(":")[0]

    return nameSpace
