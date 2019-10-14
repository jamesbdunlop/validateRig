from PySide2 import QtWidgets, QtCore
from maya import cmds


def createSourceNodeAttributeListWidget(nodes=None, qParent=None):
    if nodes is None:
        return

    w = QtWidgets.QWidget(qParent)
    w.setWindowFlags(QtCore.Qt.Popup)
    mainLayout = QtWidgets.QVBoxLayout(w)

    dv = QtWidgets.QGroupBox("Default Values")
    dvl = QtWidgets.QVBoxLayout(dv)

    # Add a list widget for each selected sourceNode
    for eachNode in nodes:
        gb = QtWidgets.QGroupBox(eachNode.split("|")[-1])
        gbl = QtWidgets.QVBoxLayout(gb)

        lw = QtWidgets.QListWidget()
        lw.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        for eachAttribute in cmds.listAttr(eachNode):
            lw.addItem(eachAttribute)

        gbl.addWidget(lw)
        dvl.addWidget(gb)

    mainLayout.addWidget(dv)

    acceptButton = QtWidgets.QPushButton('Accept')
    mainLayout.addWidget(acceptButton)

    return w
