#  Copyright (c) 2019.  James Dunlop
import validateRig.insideDCC as vr_insideDCC

MAYA_CONNECTED_NODETYPES_IGNORES = list()
if vr_insideDCC.insideMaya():
    from maya.api import OpenMaya as om2
    MAYA_CONNECTED_NODETYPES_IGNORES = [om2.MFn.kMessageAttribute,
                                        om2.MFn.kNodeGraphEditorBookmarks,
                                        om2.MFn.kNodeGraphEditorBookmarkInfo,
                                        om2.MFn.kNodeGraphEditorInfo,
                                        om2.MFn.kHyperLayout,
                                        om2.MFn.kContainer
                                        ]

JSON_EXT = ".json"
UINAME = "Validate Rig:"

DEFAULT_REPORTSTATUS = "--"

FONT_NAME = "Times"
FONT_HEADER = "Arial"
FONT_VALUE = "Times"
FONT_SIZE = 8

NODE_VALIDATION_NA = "NA"
NODE_VALIDATION_PASSED = "Passed"
NODE_VALIDATION_FAILED = "Failed"
NODE_VALIDATION_MISSINGSRC = "MISSING SRC NODE"
NODE_VALIDATION_MISSINGDEST = "MISSING DEST NODE"

TOTALHEADERCOUNT = 8
SRC_NODENAME_COLUMN = 0
SRC_ATTR_COLUMN = 1
SRC_ATTRVALUE_COLUMN = 2
DEST_NODENAME_COLUMN = 4
DEST_ATTR_COLUMN = 5
DEST_ATTRVALUE_COLUMN = 6
REPORTSTATUS_COLUMN = 7
SEPARATOR = ""

labels = {
    SRC_NODENAME_COLUMN: "SourceNodeName",
    SRC_ATTR_COLUMN: "SrcAttrName",
    SRC_ATTRVALUE_COLUMN: "SrcAttrValue",
    DEST_NODENAME_COLUMN: "DestNodeName",
    DEST_ATTR_COLUMN: "DestAttrName",
    DEST_ATTRVALUE_COLUMN: "DestAttrValue",
    REPORTSTATUS_COLUMN: "REPORT STATUS",
}

HEADER_LABELS = [""] * TOTALHEADERCOUNT
for x, label in labels.items():
    HEADER_LABELS[x] = label


MAYA_DEFAULTATTRS = [
    "translate",
    "translateX",
    "translateY",
    "translateZ",
    "rotate",
    "rotateX",
    "rotateY",
    "rotateZ",
    "scale",
    "scaleX",
    "scaleY",
    "scaleZ",
    "parentInverseMatrix",
    "parentMatrix",
    "matrix",
    "inverseMatrix",
    "worldMatrix",
    "worldInverseMatrix",
    "visibility",
]

MAYA_DEFAULTVALUEATTRIBUTE_IGNORES = ["message", "controllerObject", "dependNode"]
