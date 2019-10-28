from PySide2 import QtWidgets, QtCore
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode
from core import inside
if inside.insideMaya():
    from maya import cmds


class SourceNodeAttributeListWidget(QtWidgets.QWidget):
    addSrcNodes = QtCore.Signal(list)
    SEP = "  --->>  "

    def __init__(self, nodeName=None, sourceNode=None, parent=None):
        super(SourceNodeAttributeListWidget, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Popup)
        self._nodeName = nodeName
        self._sourceNode = sourceNode

        self._nodeData = list()

        ############################
        ## Setup the UI elements now
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Add a list widget for each selected sourceNode
        horizontalLayout = QtWidgets.QHBoxLayout()

        mainGroupBox = QtWidgets.QGroupBox(self._nodeName.split("|")[-1])
        mainGroupBoxLayout = QtWidgets.QHBoxLayout(mainGroupBox)
        horizontalLayout.addWidget(mainGroupBox)

        # Default Values
        dv = QtWidgets.QGroupBox("Default Values")
        dvl = QtWidgets.QVBoxLayout(dv)
        self.dvListWidget = QtWidgets.QListWidget()
        self.dvListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        dvl.addWidget(self.dvListWidget)

        # Connections
        dvc = QtWidgets.QGroupBox("Connections")
        dvcl = QtWidgets.QVBoxLayout(dvc)
        self.connsListWidget = QtWidgets.QListWidget()
        self.connsListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        dvcl.addWidget(self.connsListWidget)

        mainGroupBoxLayout.addWidget(dv)
        mainGroupBoxLayout.addWidget(dvc)

        # Buttons
        self.acceptButton = QtWidgets.QPushButton('Accept')
        self.acceptButton.clicked.connect(self._accept)

        # MainLayout
        self.mainLayout.addLayout(horizontalLayout)
        self.mainLayout.addWidget(self.acceptButton)

        # Store internally
        self._nodeData.append([self._nodeName, self.dvListWidget, self.connsListWidget])

        # Populate listWidgets
        self._populateDefaultValuesWidget()
        self._populateConnectionsWidget()

    def _populateDefaultValuesWidget(self):
        raise NotImplemented("Overload me!")

    def _populateConnectionsWidget(self):
        raise NotImplemented("Overload me!")

    def _accept(self):
        raise NotImplemented("Overload me!")

    def sourceNode(self):
        return self._sourceNode

    @classmethod
    def fromSourceNode(cls, sourceNode, parent=None):
        return cls(nodeName=sourceNode.name, sourceNode=sourceNode, parent=parent)


class MayaSourceNodeAttributeListWidget(SourceNodeAttributeListWidget):
    def __init__(self, nodeName=None, sourceNode=None, parent=None):
        super(MayaSourceNodeAttributeListWidget, self).__init__(nodeName=nodeName, sourceNode=sourceNode, parent=parent)

    def _populateDefaultValuesWidget(self):
        """
        Populates the listWidget from the nodeName. This should be a unique name in maya or it will fail.
        """
        for eachAttribute in sorted(cmds.listAttr(self._nodeName)):
            self.dvListWidget.addItem(eachAttribute)

        # Select existing
        if self.sourceNode() is not None:
            for nodeName in [node.name for node in self.sourceNode().iterValidityNodes() if isinstance(node, DefaultValueNode)]:
                items = self.dvListWidget.findItems(nodeName, QtCore.Qt.MatchExactly)
                for eachItem in items:
                    if not self.dvListWidget.isItemSelected(eachItem):
                        self.dvListWidget.setItemSelected(eachItem, True)

        return True

    def _populateConnectionsWidget(self):
        """
        Populates the listWidget from the nodeName. This should be a unique name in maya or it will fail.
        """
        conns = cmds.listConnections(self._nodeName, c=True, source=False, destination=True, plugs=True)
        if conns is not None:
            for x in range(0, len(conns), 2):
                self.connsListWidget.addItem("{}{}{}".format(conns[x], self.SEP, conns[x+1]))

        # Select existing
        if self.sourceNode() is not None:
            for nodeName in [n.name for n in self.sourceNode().iterValidityNodes() if isinstance(n, ConnectionValidityNode)]:
                items = self.connsListWidget.findItems(nodeName, QtCore.Qt.MatchExactly)
                for eachItem in items:
                    if not self.connsListWidget.isItemSelected(eachItem):
                        self.connsListWidget.setItemSelected(eachItem, True)
        return True

    def _accept(self):
        srcNodes = list()
        for nodeList in self._nodeData:
            nodeName = nodeList[0]

            # Create default value nodes node
            validityNodes = list()
            for eachAttr in nodeList[1].selectedItems():
                value = cmds.getAttr("{}.{}".format(nodeName, eachAttr.text()))
                dvNode = DefaultValueNode(name=eachAttr.text(), defaultValue=value)
                validityNodes.append(dvNode)

            # Create connection nodes node # [u'null2.visibility', u'null2.translate']
            for eachConnPair in nodeList[2].selectedItems():
                src, dest = eachConnPair.text().split(self.SEP)
                destAttrName = dest.split(".")[-1]
                destAttrValue = cmds.getAttr(dest)
                srcAttrName = src.split(".")[-1]
                srcAttrValue = cmds.getAttr(src)
                connNode = ConnectionValidityNode(name=dest.split(".")[0],
                                                  destAttrName=destAttrName,
                                                  destAttrValue=destAttrValue,
                                                  srcAttrName=srcAttrName,
                                                  srcAttrValue=srcAttrValue)
                validityNodes.append(connNode)

            if self.sourceNode() is None:
                srcNode = SourceNode(name=nodeName, validityNodes=validityNodes)
            else:
                srcNode = self.sourceNode()
                for eachValidityNode in validityNodes:
                    srcNode.addValidityNode(validityNode=eachValidityNode)

            srcNodes.append(srcNode)

            self.addSrcNodes.emit(srcNodes)

        self.close()

