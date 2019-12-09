# from typing import Generator
from PySide2 import QtWidgets, QtCore
from core import inside
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode
from uiStuff import validityNodeListWidget as ui_validityNodeListWidget

if inside.insideMaya():
    from maya import cmds


class MultiSourceNodeListWidgets(QtWidgets.QWidget):
    sourceNodesAccepted = QtCore.Signal(list)

    def __init__(self, title, parent=None):
        # type: (str, QtWidgets.QWidget) -> None
        super(MultiSourceNodeListWidgets, self).__init__(parent=parent)
        """This just allows pig piling up x# of listWidgets into a layout for easier handling of DnD of 
        multiple sourceNodes
        """
        self.setWindowTitle(title)
        self.setObjectName("MultiAttributeListWidget_{}".format(title))

        self.mainLayout = QtWidgets.QVBoxLayout(self)

        self._listWidgets = list()
        self.widgetsLayout = QtWidgets.QHBoxLayout()

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.acceptButton = QtWidgets.QPushButton("Accept")
        self.acceptButton.clicked.connect(self.__accept)

        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.clicked.connect(self.close)

        self.buttonLayout.addWidget(self.acceptButton)
        self.buttonLayout.addWidget(self.closeButton)

        self.mainLayout.addLayout(self.widgetsLayout)
        self.mainLayout.addLayout(self.buttonLayout)

    def addListWidget(self, listWidget):
        # type: (QtWidgets.QListWidget) -> None
        if listWidget not in self._listWidgets:
            self.widgetsLayout.addWidget(listWidget)
            self._listWidgets.append(listWidget)

    def iterListWidgets(self):
        # type: () -> Generator[QtWidgets.QListWidget]
        for eachListWidgets in self._listWidgets:
            yield eachListWidgets

    def __accept(self):
        self.sourceNodesAccepted.emit(
            [listWidget.toSourceNode() for listWidget in self.iterListWidgets()]
        )
        self.close()


class BaseSourceNodeValidityNodesSelector(QtWidgets.QWidget):
    SEP = "  --->>  "

    def __init__(self, nodeName=None, sourceNode=None, parent=None):
        # type: (str, SourceNode, QtWidgets.QWidget) -> None
        super(BaseSourceNodeValidityNodesSelector, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Popup)
        self._nodeName = nodeName
        self._sourceNode = sourceNode

        ############################
        ## Setup the UI elements now
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Add a list widget for each selected sourceNode
        mainGroupBox = QtWidgets.QGroupBox(self._nodeName)
        mainGroupBoxLayout = QtWidgets.QHBoxLayout(mainGroupBox)

        # Default Values
        defaultValuesGroupBox = QtWidgets.QGroupBox("Default Values")
        defaultValuesGroupBoxlayout = QtWidgets.QVBoxLayout(defaultValuesGroupBox)
        self.defaultValuesListWidget = (
            ui_validityNodeListWidget.ValidityNodeListWidget()
        )
        self.defaultValuesListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        defaultValuesGroupBoxlayout.addWidget(self.defaultValuesListWidget)

        # Connections
        connectionsGroupBox = QtWidgets.QGroupBox("Connections")
        connectionsGroupBoxLayout = QtWidgets.QVBoxLayout(connectionsGroupBox)
        self.connsListWidget = ui_validityNodeListWidget.ValidityNodeListWidget()
        self.connsListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        connectionsGroupBoxLayout.addWidget(self.connsListWidget)

        mainGroupBoxLayout.addWidget(defaultValuesGroupBox)
        mainGroupBoxLayout.addWidget(connectionsGroupBox)

        self.mainLayout.addWidget(mainGroupBox)

        # Store internally
        self._nodeData = (
            self._nodeName,
            self.defaultValuesListWidget,
            self.connsListWidget,
        )

        # Populate listWidgets
        self._populateDefaultValuesWidget()
        self._populateConnectionsWidget()

    def _populateDefaultValuesWidget(self):
        raise NotImplemented("Overload me!")

    def _populateConnectionsWidget(self):
        raise NotImplemented("Overload me!")

    def sourceNode(self):
        return self._sourceNode

    @classmethod
    def fromSourceNode(cls, sourceNode, parent=None):
        # type: (SourceNode, QtWidgets.QWidget) -> BaseSourceNodeValidityNodesSelector
        return cls(nodeName=sourceNode.longName, sourceNode=sourceNode, parent=parent)


class MayaValidityNodesSelector(BaseSourceNodeValidityNodesSelector):
    def __init__(self, nodeName=None, sourceNode=None, parent=None):
        # type: (str, SourceNode, QtWidgets.QWidget) -> None
        super(MayaValidityNodesSelector, self).__init__(
            nodeName=nodeName, sourceNode=sourceNode, parent=parent
        )

    def _populateDefaultValuesWidget(self):
        """Populates the listWidget from the nodeName. This should be a unique name in maya or it will fail."""
        for eachAttribute in sorted(cmds.listAttr(self._nodeName)):
            self.defaultValuesListWidget.addItem(eachAttribute)

        # Select existing
        if self.sourceNode() is None:
            return

        nodeNames = [
            node.name
            for node in self.sourceNode().iterChildren()
            if isinstance(node, DefaultValueNode)
        ]
        if self.sourceNode() is not None:
            for nodeName in nodeNames:
                items = self.defaultValuesListWidget.findItems(
                    nodeName, QtCore.Qt.MatchExactly
                )
                for eachItem in items:
                    if not self.defaultValuesListWidget.isItemSelected(eachItem):
                        self.defaultValuesListWidget.setItemSelected(eachItem, True)

        return True

    def _populateConnectionsWidget(self):
        """Populates the listWidget from the nodeName. This should be a unique name in maya or it will fail."""
        conns = cmds.listConnections(
            self._nodeName, c=True, source=False, destination=True, plugs=True
        )
        if conns is not None:
            for x in range(0, len(conns), 2):
                self.connsListWidget.addItem(
                    "{}{}{}".format(conns[x], self.SEP, conns[x + 1])
                )

        # Select existing
        if self.sourceNode() is not None:
            for nodeName in [
                n.name
                for n in self.sourceNode().iterChildren()
                if isinstance(n, ConnectionValidityNode)
            ]:
                items = self.connsListWidget.findItems(nodeName, QtCore.Qt.MatchExactly)
                for eachItem in items:
                    if not self.connsListWidget.isItemSelected(eachItem):
                        self.connsListWidget.setItemSelected(eachItem, True)

    def __getValidityNodesFromDefaultValuesListWidget(
        self, nodeName, defaultValuesListWidget
    ):
        # type: (str, QtWidgets.QListWidget) -> list[DefaultValueNode]
        """
        Args:
            nodeName: name of the node to query in maya (this is the destination node not the sourceNode.name)
        """
        nodes = list()
        for eachAttr in defaultValuesListWidget.selectedItems():
            value = cmds.getAttr("{}.{}".format(nodeName, eachAttr.text()))
            dvNode = DefaultValueNode(name=eachAttr.text(), defaultValue=value)
            nodes.append(dvNode)

        return nodes

    def __getValidityNodesFromConnectionsListWidget(self, connectionsListWidget):
        # type: (QtWidgets.QListWidget) -> list[ConnectionValidityNode]
        nodes = list()
        for eachConnPair in connectionsListWidget.selectedItems():
            src, dest = eachConnPair.text().split(self.SEP)

            connectionNode = ConnectionValidityNode(
                name=dest.split(".")[0], longName=dest
            )
            connectionNode.destAttrName = dest.split(".")[-1]
            connectionNode.destAttrValue = cmds.getAttr(dest)
            connectionNode.srcAttrName = src.split(".")[-1]
            connectionNode.srcAttrValue = cmds.getAttr(src)

            nodes.append(connectionNode)

        return nodes

    def toSourceNode(self):
        # type: () -> SourceNode
        nodeName, defaultValuesListWidget, connsListWidget = self._nodeData

        # Collect validityNode children for the SourceNode into a list
        validityNodes = list()
        validityNodes += self.__getValidityNodesFromDefaultValuesListWidget(
            nodeName, defaultValuesListWidget
        )
        validityNodes += self.__getValidityNodesFromConnectionsListWidget(
            connsListWidget
        )

        if self.sourceNode() is None:
            return SourceNode(
                name=nodeName, longName=nodeName, validityNodes=validityNodes
            )
        else:
            self.sourceNode().addChild(validityNodes)
            return self.sourceNode()
