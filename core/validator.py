import logging
# from typing import Generator
from PySide2 import QtCore
from PySide2.QtCore import Signal
from core import inside
from core import mayaValidation
from core import parser as c_parser
from core.nodes import SourceNode
from vrConst import serialization as c_serialization
from vrConst import constants as vrc_constants

logger = logging.getLogger(__name__)


class Validator(QtCore.QObject):
    validate = Signal(QtCore.QObject)
    repair = Signal(QtCore.QObject)

    def __init__(self, name, namespace="", nodes=None):
        # type: (str, str, list) -> None
        QtCore.QObject.__init__(self, None)
        self._name = name  # name of the validator.
        self._namespace = namespace
        self._nodes = (
            nodes or list()
        )  # list of SourceNodes with ConnectionValidityNodes
        self._status = vrc_constants.NODE_VALIDATION_PASSED

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        """
        Args:
            name: name of the validator
        """
        if type(name) != str:
            raise TypeError("name is not of type str!")

        self._name = name

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace):
        # type: (str) -> None
        self._namespace = namespace

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def failed(self):
        return self.status == vrc_constants.NODE_VALIDATION_FAILED

    @property
    def passed(self):
        return self.status == vrc_constants.NODE_VALIDATION_PASSED

    def findSourceNodeByLongName(self, name):
        # type: (str) -> SourceNode
        for eachNode in self.iterSourceNodes():
            if eachNode.longName == name:
                return eachNode

    def sourceNodeExists(self, sourceNode):
        # type: (SourceNode) -> bool
        sourceNodeNames = [sn.longName for sn in self._nodes]

        return sourceNode.longName in sourceNodeNames

    def sourceNodeLongNameExists(self, sourceNodeLongName):
        # type: (str) -> bool
        sourceNodeNames = [n.longName for n in self._nodes]
        logger.info(
            "{} sourceNodeNames: {}".format(sourceNodeLongName, sourceNodeNames)
        )
        return sourceNodeLongName in sourceNodeNames

    def replaceExistingSourceNode(self, sourceNode):
        # type: (SourceNode) -> bool
        """Replace an existing index in the list with the sourceNode"""
        for x, node in enumerate(self._nodes):
            if node.longName == sourceNode.longName:
                self._nodes[x] = sourceNode
                return True

        return False

    def addSourceNode(self, sourceNode, force=False):
        # type: (SourceNode, bool) -> bool
        if not self.sourceNodeExists(sourceNode):
            self._nodes.append(sourceNode)
            return True

        if self.sourceNodeExists(sourceNode) is not None and force:
            return self.replaceExistingSourceNode(sourceNode)

        if self.sourceNodeExists(sourceNode) and not force:
            raise IndexError(
                "%s already exists in validator. Use force=True if you want to overwrite existing!"
                % sourceNode
            )

        return False

    def addSourceNodeFromData(self, data):
        # type: (dict) -> SourceNode
        sourceNode = SourceNode.fromData(data)
        self.addSourceNode(sourceNode)

        return sourceNode

    def removeSourceNode(self, sourceNode):
        # type: (SourceNode) -> bool
        for eachSourceNode in self.iterSourceNodes():
            if eachSourceNode == sourceNode:
                self._nodes.remove(eachSourceNode)
                return True

        return False

    def iterSourceNodes(self):
        # type: (SourceNode) -> Generator[SourceNode]
        for eachNode in self._nodes:
            yield eachNode

    def validateSourceNodes(self):
        self.validate.emit(self)

    def repairSourceNodes(self):
        self.repair.emit(self)

    def toData(self):
        data = dict()
        data[c_serialization.KEY_VALIDATOR_NAME] = self.name
        data[c_serialization.KEY_VALIDATOR_NODES] = list()
        for eachNode in self.iterSourceNodes():
            data[c_serialization.KEY_VALIDATOR_NODES].append(eachNode.toData())

        return data

    def to_fileJSON(self, filePath):
        logger.info("Writing validator to: %s" % filePath)
        c_parser.write(filepath=filePath, data=self.toData())
        logger.info("Successfully wrote validator to: %s" % filePath)

        return True

    @classmethod
    def fromData(cls, name, data):
        inst = cls(name)
        for sourceNodeData in data.get(c_serialization.KEY_VALIDATOR_NODES, list()):
            inst.addSourceNodeFromData(sourceNodeData)

        return inst

    def __repr__(self):
        return "%s" % self.name


def createValidator(name, data=None):
    # type: (str, dict) -> Validator
    """
    Args:
        name: The name for the validator. Eg: MyCat
    """
    if data is None:
        validator = Validator(name=name)
    else:
        validator = Validator.fromData(name, data)

    if inside.insideMaya():
        validator.validate.connect(mayaValidation.validateSourceNodes)
        validator.repair.connect(mayaValidation.repairSourceNodes)

    else:
        msg = lambda x: logger.info(x)
        validator.validate.connect(msg("No stand alone validation is possible!!"))

    return validator
