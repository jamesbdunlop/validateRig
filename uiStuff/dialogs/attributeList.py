from PySide2 import QtWidgets, QtCore
from core.nodes import SourceNode, DefaultValueNode, ConnectionValidityNode
from maya import cmds


class SourceNodeAttributeListWidget(QtWidgets.QWidget):
    addSrcNodes = QtCore.Signal(list)
    SEP = "  --->>  "

    def __init__(self, nodes=None, qParent=None):
        super(SourceNodeAttributeListWidget, self).__init__(parent=qParent)
        if nodes is None:
            return

        self._nodeData = list()

        self.setWindowFlags(QtCore.Qt.Popup)
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Add a list widget for each selected sourceNode
        for eachNode in nodes:
            subLayout = QtWidgets.QHBoxLayout()

            ngb = QtWidgets.QGroupBox(eachNode.split("|")[-1])
            ngbhl = QtWidgets.QHBoxLayout(ngb)

            # DV
            dv = QtWidgets.QGroupBox("Default Values")
            dvl = QtWidgets.QVBoxLayout(dv)

            self.lw = QtWidgets.QListWidget()
            self.lw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

            for eachAttribute in cmds.listAttr(eachNode):
                self.lw.addItem(eachAttribute)
            dvl.addWidget(self.lw)

            # Connections
            dvc = QtWidgets.QGroupBox("Connections")
            dvcl = QtWidgets.QVBoxLayout(dvc)
            self.lwc = QtWidgets.QListWidget()
            self.lwc.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

            conns = cmds.listConnections(eachNode, c=True, source=True, destination=True, plugs=True)
            if conns is not None:
                for x in xrange(0, len(conns), 2):
                    self.lwc.addItem("{}{}{}".format(conns[x], self.SEP, conns[x+1]))

            dvcl.addWidget(self.lwc)

            ngbhl.addWidget(dv)
            ngbhl.addWidget(dvc)

            subLayout.addWidget(ngb)
            self.mainLayout.addLayout(subLayout)

            # Store internally
            self._nodeData.append([eachNode, self.lw, self.lwc])

        self.acceptButton = QtWidgets.QPushButton('Accept')
        self.acceptButton.clicked.connect(self._accept)

        self.mainLayout.addWidget(self.acceptButton)

    def _accept(self):
        srcNodes = list()
        for eachNodeList in self._nodeData:
            nodeName = eachNodeList[0]

            # Create default value nodes node
            validityNodes = list()
            for eachAttr in eachNodeList[1].selectedItems():
                value = cmds.getAttr("{}.{}".format(nodeName, eachAttr.text()))
                dvNode = DefaultValueNode(name=eachAttr.text(), defaultValue=value)
                validityNodes.append(dvNode)

            # Create connection nodes node # [u'null2.visibility', u'null2.translate']
            for eachConnPair in eachNodeList[2].selectedItems():
                src, dest = eachConnPair.text().split(self.SEP)
                destAttrName = dest.split(".")[-1]
                destAttrValue = cmds.getAttr(dest)
                srcAttributeName = src.split(".")[-1]
                srcAttributeValue = cmds.getAttr(src)
                connNode = ConnectionValidityNode(name=dest.split(".")[0],
                                                  attributeName=destAttrName,
                                                  attributeValue=destAttrValue,
                                                  srcAttributeName=srcAttributeName,
                                                  srcAttributeValue=srcAttributeValue)
                validityNodes.append(connNode)

            srcNode = SourceNode(name=nodeName, validityNodes=validityNodes)
            srcNodes.append(srcNode)

        self.addSrcNodes.emit(srcNodes)
        self.close()


    def fromSourceNodes(self, srcNodes):
        # TODO be able to instance this widget from an existing sourceNode list and select existing in the validator
        # so we can force it back into the validator with new selections etc.
        pass
