from const import serialization as c_s

SRC_NODENAME = "myCtrl_ctrl"
SRC_ATTRNAME = "showCloth"
SRC_ATTRVALUE = True
SRC_NODETYPE = c_s.NT_SOURCENODE

VALIDITY_NODENAME = "geo_hrc"
VALIDITY_NODETYPE = c_s.NT_CONNECTIONVALIDITY
VALIDITY_DEST_ATTRNAME = "visibility"
VALIDITY_DEST_ATTRVALUE = True

VALIDATOR_NAME = "TestValidator"
