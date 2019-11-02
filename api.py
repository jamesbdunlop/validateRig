import sys
from core import validator
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode
import app as validateRigApplication
from PySide2 import QtWidgets

def createValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return validator.Validator(name=name)


def createMayaValidator(name):
    """

    :param name:`str`
    :return: `Validator`
    """

    return validator.MayaValidator(name=name)


def createSourceNode(name, validityNodes=None):
    """

    :param name: `str`
    :param validityNodes: `list` of either DefaultValueNodes or ConnectionValidityNodes
    :return:
    """
    return SourceNode(name=name, validityNodes=validityNodes)


def createDefaultValueNode(name, value):
    return DefaultValueNode(name=name, value=value)


def createConnectionValidityNode(
    name,
    sourceNodeAttributeName,
    sourceNodeAttributeValue,
    desinationNodeAttributeName,
    destinationNodeAttributeValue,
):
    """

    :param name: `str`
    :param sourceNodeAttributeName: `str`
    :param sourceNodeAttributeValue: `int` | `float` | `bool` | etc
    :param desinationNodeAttributeName: `srt`
    :param destinationNodeAttributeValue: `int` | `float` | `bool` | etc
    :return: `ConnectionValidityNode`
    """
    node = ConnectionValidityNode(name=name)
    node.destAttrName = desinationNodeAttributeName
    node.destAttrValue = destinationNodeAttributeValue
    node.srcAttrName = sourceNodeAttributeName
    node.srcAttrValue = sourceNodeAttributeValue

    return node

def uiFromValidtators(name, theme="core", themecolor="", parent=None, validators=None):
    """

    :param name: `str`
    :param validator: `list` of Validator instances
    """
    app = QtWidgets.QApplication(sys.argv).instance()
    win = validateRigApplication.ValidationUI(name, theme=theme, themecolor=themecolor, parent=parent)
    for eachValidator in validators:
        win.addValidatorFromData(eachValidator.toData())

    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    uiFromValidtators(name="testUI", validators=[createValidator("test")])

