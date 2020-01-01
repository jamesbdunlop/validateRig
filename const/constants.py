#  Copyright (c) 2019.  James Dunlop
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

MAYA_DEFAULTVALUEATTRIBUTE_IGNORES = [
    "message",
    "controllerObject",
    "dependNode"
    ]

MAYA_CONNECTED_NODETYPES_IGNORES = [
    "nodeGraphEditorInfo"
    ]
