#  Copyright (c) 2019.  James Dunlop
# pragma: no cover
import logging
from const import serialization as c_serialization
from const import constants as vrc_constants
from core.maya import utils as cm_utils

logger = logging.getLogger(__name__)




##############################################
# VALIDATE
def validateValidatorSourceNodes(validator):
    # type: (Validator) -> None
    validator.status = vrc_constants.NODE_VALIDATION_PASSED
    for eachSourceNode in validator.iterSourceNodes():
        eachSourceNode.status = vrc_constants.NODE_VALIDATION_PASSED
        srcNodeName = eachSourceNode.longName
        if not cm_utils.exists(srcNodeName):
            continue

        defaultStatus = validateDefaultNodes(eachSourceNode)
        connectionStatus = validateConnectionNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if not passed:
            eachSourceNode.status = vrc_constants.NODE_VALIDATION_FAILED
            validator.status = vrc_constants.NODE_VALIDATION_FAILED


def validateDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        defaultNodeLongName = eachValidationNode.longName
        defaultAttrName = eachValidationNode.name
        defaultNodeValue = eachValidationNode.defaultValue

        attrValue = cm_utils.getAttrValue(defaultNodeLongName, defaultAttrName)

        result = defaultNodeValue == attrValue
        if not setValidationStatus(eachValidationNode, result):
            passed = False

    return passed


def validateConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool
    passed = True
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue

        result = None
        # TODO om2

        if not setValidationStatus(eachValidationNode, result):
            passed = False

    return passed


##############################################
# REPAIR
def repairValidatorSourceNodes(validator):
    # type: (Validator) -> None
    for eachSourceNode in validator.iterSourceNodes():
        srcNodeName = eachSourceNode.longName
        if not cm_utils.exists(srcNodeName):
            continue

        defaultStatus = repairDefaultNodes(eachSourceNode)
        connectionStatus = repairConnectionNodes(eachSourceNode)

        passed = all((defaultStatus, connectionStatus))
        if passed:
            validator.status = vrc_constants.NODE_VALIDATION_FAILED
        else:
            validator.status = vrc_constants.NODE_VALIDATION_PASSED


def repairDefaultNodes(sourceNode):
    # type: (SourceNode) -> bool
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.status == vrc_constants.NODE_VALIDATION_PASSED:
            continue
        if eachValidationNode.nodeType != c_serialization.NT_DEFAULTVALUE:
            continue

        # sourceAttrName = eachValidationNode.longName
        # defaultValue = eachValidationNode.defaultValue
        # if isinstance(defaultValue, list):
        #     cmds.setAttr(
        #         sourceAttrName, defaultValue[0], defaultValue[1], defaultValue[2]
        #     )
        # else:
        #     cmds.setAttr(sourceAttrName, eachValidationNode.defaultValue)
        # TODO om2

        setValidationStatus(eachValidationNode, True)

    return True


def repairConnectionNodes(sourceNode):
    # type: (SourceNode) -> bool
    for eachValidationNode in sourceNode.iterDescendants():
        if eachValidationNode.nodeType != c_serialization.NT_CONNECTIONVALIDITY:
            continue
        if eachValidationNode.status == vrc_constants.NODE_VALIDATION_PASSED:
            continue

        # sourceAttrName = "{}.{}".format(
        #     eachValidationNode.parent.longName, eachValidationNode.srcAttrName
        # )
        # destAttrName = "{}.{}".format(
        #     eachValidationNode.longName, eachValidationNode.destAttrName
        # )
        #
        # cmds.connectAttr(sourceAttrName, destAttrName, force=True)
        # TODO om2
        setValidationStatus(eachValidationNode, True)

    return True


def setValidationStatus(validationNode, result):
    # type: (ValidationNode, bool) -> bool
    if result:
        validationNode.status = vrc_constants.NODE_VALIDATION_PASSED
        return result

    validationNode.status = vrc_constants.NODE_VALIDATION_FAILED
    return result
