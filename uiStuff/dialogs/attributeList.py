from PySide2 import QtWidgets, QtCore
from maya import cmds


class SourceNodeAttributeListWidget(QtWidgets.QWidget):
    def __init__(self, nodes=None, qParent=None):
        super(SourceNodeAttributeListWidget, self).__init__(parent=qParent)

        if nodes is None:
            return

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

            lw = QtWidgets.QListWidget()
            lw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

            for eachAttribute in cmds.listAttr(eachNode):
                lw.addItem(eachAttribute)
            dvl.addWidget(lw)

            # Connections
            dvc = QtWidgets.QGroupBox("Connections")
            dvcl = QtWidgets.QVBoxLayout(dvc)
            lwc = QtWidgets.QListWidget()
            lwc.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            for eachConnection in cmds.listConnections(eachNode, plugs=True):
                lwc.addItem(eachConnection)

            dvcl.addWidget(lwc)

            ngbhl.addWidget(dv)
            ngbhl.addWidget(dvc)

            subLayout.addWidget(ngb)
            self.mainLayout.addLayout(subLayout)

        self.acceptButton = QtWidgets.QPushButton('Accept')
        self.mainLayout.addWidget(self.acceptButton)

