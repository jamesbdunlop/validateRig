#  Copyright (c) 2019.  James Dunlop
import logging
from PySide2 import QtWidgets, QtCore
from validateRig.core.nodes import SourceNode
from validateRig.uiElements import validityNodeListWidget as vruie_validityNodeListWidget

logger = logging.getLogger(__name__)


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

        mainLayout = QtWidgets.QVBoxLayout(self)

        self.sharedAttributes = QtWidgets.QRadioButton("Use first for All")
        self.sharedAttributes.toggled.connect(self._toggleSharedAttributes)

        self._listWidgets = list()

        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidgetLayout = QtWidgets.QVBoxLayout(self.scrollWidget)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        buttonLayout = QtWidgets.QHBoxLayout()
        acceptButton = QtWidgets.QPushButton("Accept")
        acceptButton.clicked.connect(self.__accept)

        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close)

        buttonLayout.addWidget(acceptButton)
        buttonLayout.addWidget(closeButton)

        # mainLayout.addLayout(self.listWidgetsLayout)
        mainLayout.addWidget(self.sharedAttributes)
        mainLayout.addWidget(self.scrollArea)
        mainLayout.addLayout(buttonLayout)

        self.resize(800, 400)

    def addListWidget(self, listWidget):
        # type: (QtWidgets.QListWidget) -> None
        if listWidget not in self._listWidgets:
            self._listWidgets.append(listWidget)
            self.scrollWidgetLayout.addWidget(listWidget)

    def _toggleSharedAttributes(self, sender):
        # Remove all children in the list widget
        for i in reversed(range(self.scrollWidgetLayout.count())):
            self.scrollWidgetLayout.itemAt(i).widget().setParent(None)
        if sender:
            self.scrollWidgetLayout.addWidget(self._listWidgets[0])
            self._listWidgets[0].connectionsGroupBox.hide()
        else:
            for listWidget in self._listWidgets:
                self.scrollWidgetLayout.addWidget(listWidget)
            self._listWidgets[0].connectionsGroupBox.show()

    def iterListWidgets(self):
        # type: () -> Generator[QtWidgets.QListWidget]
        for eachListWidgets in self._listWidgets:
            yield eachListWidgets

    def __accept(self):
        srcListWidget = None
        if self.sharedAttributes.isChecked():
            srcListWidget = self._listWidgets[0]

        logger.debug("Emit sourceNodes list()")
        self.sourceNodesAccepted.emit(
            [
                listWidget.toSourceNode(srcListWidget)
                for listWidget in self.iterListWidgets()
            ]
        )

        self.close()


class BaseSourceNodeValidityNodesSelector(QtWidgets.QWidget):
    SEP = " |->| "

    def __init__(self, longNodeName=None, sourceNode=None, parent=None):
        # type: (str, SourceNode, QtWidgets.QWidget) -> None
        super(BaseSourceNodeValidityNodesSelector, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Popup)
        self._longNodeName = longNodeName
        self._sourceNode = sourceNode

        ############################
        ## Setup the UI elements now
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Add a list widget for each selected sourceNode
        mainGroupBox = QtWidgets.QGroupBox(self._longNodeName)
        mainGroupBoxLayout = QtWidgets.QHBoxLayout(mainGroupBox)
        mainGroupBoxLayoutSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, None)
        mainGroupBoxLayoutSplitter.setStretchFactor(1, 1)
        mainGroupBoxLayoutSplitter.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        # Default Values
        defaultValuesGroupBox = QtWidgets.QGroupBox("Default Values")
        defaultValuesGroupBoxlayout = QtWidgets.QVBoxLayout(defaultValuesGroupBox)
        self.defaultValuesListWidget = (
            vruie_validityNodeListWidget.ValidityNodeListWidget()
        )
        self.defaultValuesListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        defaultValuesGroupBoxlayout.addWidget(self.defaultValuesListWidget)

        # Connections
        connectionsGroupBox = QtWidgets.QGroupBox(
            "Connections"
        )  # we hide this when showing only the one in the list all
        connectionsGroupBoxLayout = QtWidgets.QVBoxLayout(connectionsGroupBox)
        self.connsListWidget = vruie_validityNodeListWidget.ValidityNodeListWidget()
        self.connsListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        connectionsGroupBoxLayout.addWidget(self.connsListWidget)

        mainGroupBoxLayoutSplitter.addWidget(defaultValuesGroupBox)
        mainGroupBoxLayoutSplitter.addWidget(connectionsGroupBox)
        mainGroupBoxLayout.addWidget(mainGroupBoxLayoutSplitter)

        self.mainLayout.addWidget(mainGroupBox)

        # Store internally
        self._nodeData = (
            self._longNodeName,
            self.defaultValuesListWidget,
            self.connsListWidget,
        )



    def _populateDefaultValuesWidget(self):
        raise NotImplemented("Overload me!")

    def _populateConnectionsWidget(self):
        raise NotImplemented("Overload me!")

    def sourceNode(self):
        return self._sourceNode

    @classmethod
    def fromSourceNode(cls, sourceNode, parent=None):
        # type: (SourceNode, QtWidgets.QWidget) -> BaseSourceNodeValidityNodesSelector
        return cls(
            longNodeName=sourceNode.longName, sourceNode=sourceNode, parent=parent
        )


