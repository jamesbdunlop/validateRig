#  Copyright (c) 2019.  James Dunlop
from validateRig.const import serialization as vrconst_serialization

NODENAME = "myNodeName"

SRC_NODENAME = "myCtrl_ctrl"
SRC_ATTRNAME = "showCloth"
SRC_ATTRVALUE = True
SRC_NODETYPE = vrconst_serialization.NT_SOURCENODE

VALIDITY_NODENAME = "geo_hrc"
VALIDITY_NODETYPE = vrconst_serialization.NT_CONNECTIONVALIDITY
VALIDITY_DEST_ATTRNAME = "visibility"
VALIDITY_DEST_ATTRVALUE = True

DEFAULT_NODENAME = "geo_hrc"
DEFAULT_NODEVALUE = 500
DEFAULT_NODETYPE = vrconst_serialization.NT_DEFAULTVALUE

VALIDATOR_NAME = "TestValidator"
VALIDATOR_NAMESPACE = "testNamespace"
