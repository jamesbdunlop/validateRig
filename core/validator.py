import logging
from PySide2 import QtCore
from PySide2.QtCore import Signal
from core import parser as c_parser
from core import inside
from core.nodes import SourceNode
from const import serialization as c_serialization
from core import mayaValidation

logger = logging.getLogger(__name__)


class Validator(QtCore.QObject):
    validate = Signal(list)

    def __init__(self, name, namespace="", nodes=None):
        QtCore.QObject.__init__(self, None)
        self._name = name  # name of the validator.
        self._namespace = namespace
        self._nodes = (
            nodes or list()
        )  # list of SourceNodes with ConnectionValidityNodes

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """

        :param name:`str` name of the validator
        :return:
        """
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._name = name

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        self._namespace = namespace

    def findSourceNodeByLongName(self, name):
        """

        :param name: `str`
        :return: `SourceNode`
        """
        for eachNode in self.iterSourceNodes():
            if eachNode.longName == name:
                return eachNode

    def sourceNodeExists(self, sourceNode):
        """

        :param sourceNode: `SourceNode`
        :return:
        """
        sourceNodeNames = [sn.longName for sn in self._nodes]

        return sourceNode.longName in sourceNodeNames

    def sourceNodeNameExists(self, sourceNodeLongName):
        """

        :param sourceNodeLongName: `str`
        :return:
        """
        sourceNodeNames = [n.longName for n in self._nodes]
        logger.debug("{} sourceNodeNames: {}".format(sourceNodeLongName, sourceNodeNames))
        return sourceNodeLongName in sourceNodeNames

    def replaceExistingSourceNode(self, sourceNode):
        """
        Replace an existing index in the list with the sourceNode
        :param sourceNode: `SourceNode`
        :return: `bool`
        """
        for x, node in enumerate(self._nodes):
            if node.longName == sourceNode.longName:
                self._nodes[x] = sourceNode
                return sourceNode

    def addSourceNode(self, sourceNode, force=False):
        """
        :param sourceNode: `SourceNode`
        :param force: `bool`
        """

        if not self.sourceNodeExists(sourceNode):
            self._nodes.append(sourceNode)
            return sourceNode

        if self.sourceNodeExists(sourceNode) is not None and force:
            return self.replaceExistingSourceNode(sourceNode)

        if self.sourceNodeExists(sourceNode) and not force:
            raise IndexError(
                "%s already exists in validator. Use force=True if you want to overwrite existing!"
                % sourceNode
            )

    def addSourceNodeFromData(self, data):
        """

        :param data: `dict`
        :return: `SourceNode`
        """
        sourceNode = SourceNode.fromData(data)
        self.addSourceNode(sourceNode)

        return sourceNode

    def removeSourceNode(self, sourceNode):
        for eachSourceNode in self.iterSourceNodes():
            if eachSourceNode == sourceNode:
                self._nodes.remove(eachSourceNode)
                return True

        return False

    def iterSourceNodes(self):
        for eachNode in self._nodes:
            yield eachNode

    def validateSourceNodes(self):
        self.validate.emit(list(self.iterSourceNodes()))

    def toData(self):
        data = dict()
        data[c_serialization.KEY_VALIDATOR_NAME] = self.name
        data[c_serialization.KEY_VALIDATOR_NODES] = list()
        for eachNode in self.iterSourceNodes():
            data[c_serialization.KEY_VALIDATOR_NODES].append(eachNode.toData())

        return data

    @classmethod
    def fromData(cls, data):
        """

        :param data: `dict`
        """
        pass

    @classmethod
    def from_fileJSON(cls, filePath):
        data = c_parser.read(filepath=filePath)
        return cls.fromData(cls, data)

    def to_fileJSON(self, filePath):
        logger.info("Writing validator to: %s" % filePath)
        c_parser.write(filepath=filePath, data=self.toData())
        logger.info("Successfully wrote validator to: %s" % filePath)
        return True

    def __repr__(self):
        return "%s" % self.name


def getValidator(name):
    """

    :param name: The name for the validator. Eg: MyCat
    :type name: `str`
    :return: `Validator`
    """
    validator = Validator(name=name)

    if inside.insideMaya():
        validator.validate.connect(mayaValidation.validateSourceNodes)
    else:
        validator.validate.connect(_printFailedStandAloneMsg)

    return validator


def _printFailedStandAloneMsg():
    print("No stand alone validation is possible!!")
