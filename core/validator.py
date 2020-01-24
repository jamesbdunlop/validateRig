#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtCore
from PySide2.QtCore import Signal
from const import serialization as c_serialization
from const import constants as vrc_constants
from core import parser as c_parser
from core.nodes import SourceNode

logger = logging.getLogger(__name__)


class Validator(QtCore.QObject):
    validate = Signal(QtCore.QObject)
    repair = Signal(QtCore.QObject)
    displayNameChanged = Signal(bool)

    def __init__(self, name, nameSpace="", nodes=None):
        # type: (str, str, list) -> None
        QtCore.QObject.__init__(self, None)
        self._name = name  # name of the validator.
        self._nameSpace = nameSpace # This can be mutated by UI
        self._nameSpaceOnCreate = nameSpace # this doesn't change after creation
        self._nodes = (
            nodes or list()
        )  # list of SourceNodes with ConnectionValidityNodes
        self._status = vrc_constants.NODE_VALIDATION_FAILED

    @property
    def nameSpaceOnCreate(self):
        return self._nameSpaceOnCreate

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
        self._name = name

    @property
    def nameSpace(self):
        return self._nameSpace

    @nameSpace.setter
    def nameSpace(self, nameSpace):
        # type: (str, int) -> None
        self._nameSpace = nameSpace

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

    def findSourceNodeByLongName(self, longName):
        # type: (str) -> SourceNode
        for eachNode in self.iterSourceNodes():
            if eachNode.longName == longName:
                return eachNode

    def sourceNodeExists(self, sourceNode):
        # type: (SourceNode) -> bool
        exists = self.sourceNodeLongNameExists(sourceNode.longName)

        return exists

    def sourceNodeLongNameExists(self, sourceNodeLongName):
        # type: (str) -> bool
        sourceNodeNames = [n.longName for n in self.iterSourceNodes()]
        exists = sourceNodeLongName in sourceNodeNames

        return exists

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

    def addSourceNodes(self, sourceNodes, force=False):
        # type: (list[SourceNode], bool) -> None
        for eachSourcenode in sourceNodes:
            self.addSourceNode(eachSourcenode, force)

        return True

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

    def validateValidatorSourceNodes(self):  # pragma: no cover
        self.validate.emit(self)

    def repairValidatorSourceNodes(self):  # pragma: no cover
        self.repair.emit(self)

    def toggleLongNodeNames(self, toggle):
        # type (bool) -> None
        if not toggle:
            self._setAllNodeDisplayNamesToNamespaceShortName()
        else:
            self._setAllNodeDisplayNamesAsLongName()

        self.displayNameChanged.emit(True)

    def _setAllNodeDisplayNamesAsLongName(self):
        for eachSrcNode in self.iterSourceNodes():
            eachSrcNode.displayName = eachSrcNode.longName
            for eachChild in eachSrcNode.iterDescendants():
                if eachChild.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                    if ":" in eachChild.longName:
                        eachChild.displayName = eachChild.longName

        self.displayNameChanged.emit(True)

    def _setAllNodeDisplayNamesToNamespaceShortName(self):
        for eachSrcNode in self.iterSourceNodes():
            eachSrcNode.displayName = self.__createNameSpacedShortName(eachSrcNode)
            for eachChild in eachSrcNode.iterDescendants():
                if eachChild.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                    if ":" in eachChild.longName:
                        eachChild.displayName = self.__createNameSpacedShortName(eachChild)

    def __createNameSpacedShortName(self, node):
        # type: (Node) -> str
        shortName = "{}:{}".format(self.nameSpace, node.name) if self.nameSpace else node.name
        return shortName

    def updateNameSpaceInLongName(self, nameSpace):
        # type: (str) -> None
        for eachSrcNode in self.iterSourceNodes():
            newLongName = self.replaceNameSpace(eachSrcNode.longName, nameSpace)
            eachSrcNode.longName = newLongName

            for eachChild in eachSrcNode.iterDescendants():
                if eachChild.nodeType == c_serialization.NT_CONNECTIONVALIDITY:
                    newLongName = self.replaceNameSpace(eachChild.longName, nameSpace)
                    eachChild.longName = newLongName

    def replaceNameSpace(self, nodeLongName, nameSpace):
        # type: (str, str) -> str
        """This is slightly arse about face. the namespace is the old namespace to replace by the newly set self.nameSpace"""
        tokens = nodeLongName.split("{}:".format(nameSpace))
        if self.nameSpace:
            newNameSpace = "{}:".format(self.nameSpace)
        else:
            newNameSpace = ""

        newName = newNameSpace.join(tokens)

        return newName

    def toData(self):
        data = dict()
        data[c_serialization.KEY_VALIDATOR_NAME] = self.name
        data[c_serialization.KEY_VALIDATORNAMESPACE] = self.nameSpace
        data[c_serialization.KEY_VALIDATOR_NODES] = list()
        for eachNode in self.iterSourceNodes():
            data[c_serialization.KEY_VALIDATOR_NODES].append(eachNode.toData())

        return data

    def to_fileJSON(self, filePath):
        c_parser.write(filepath=filePath, data=self.toData())

        return True

    @classmethod
    def fromData(cls, name, data):
        nameSpace = data.get(c_serialization.KEY_VALIDATORNAMESPACE, "")
        if name is None:
            name = data.get(c_serialization.KEY_NODENAME, None)

        inst = cls(name, nameSpace)
        for sourceNodeData in data.get(c_serialization.KEY_VALIDATOR_NODES, list()):
            inst.addSourceNodeFromData(sourceNodeData)

        return inst

    def __repr__(self):
        return "%s" % self.name
