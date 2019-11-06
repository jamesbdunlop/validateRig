#  Copyright (c) 2019.  James Dunlop

import logging
import sys
from PySide2 import QtWidgets, QtCore


logger = logging.getLogger(__name__)


class ValidityNodeListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        """

        :param contextMenu: `QMenu`
        :param validator: `Validator`
        :param parent: `QtParent`
        """
        super(ValidityNodeListWidget, self).__init__(parent=parent)
        self._mainLayout = QtWidgets.QVBoxLayout(self)

        self._listWidget = QtWidgets.QListWidget()
        self._listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # FilterBox
        filterLayout = QtWidgets.QHBoxLayout()
        self._filterInput = QtWidgets.QLineEdit()
        self._filterInput.setPlaceholderText("Search....")
        self._filterInput.textChanged.connect(self._updateFilter)

        clearSearchButton = QtWidgets.QPushButton("Clear")
        clearSearchButton.clicked.connect(self.__clearSearch)

        self.hideByCustomFiltersButton = QtWidgets.QPushButton("Hide Defaults")
        self.hideByCustomFiltersButton.clicked.connect(self.__hideDefaults)
        self.unhideByCustomFiltersButton = QtWidgets.QPushButton("unHide Defaults")
        self.unhideByCustomFiltersButton.setHidden(True)
        self.unhideByCustomFiltersButton.clicked.connect(self.__unhideDefaults)

        self.hideBySelectedButton = QtWidgets.QPushButton("show Only Selected")
        self.hideBySelectedButton.clicked.connect(self.__hideSelected)
        self.showAllButton = QtWidgets.QPushButton("show All")
        self.showAllButton.setHidden(True)
        self.showAllButton.clicked.connect(self.__showAll)

        filterLayout.addWidget(self._filterInput)
        filterLayout.addWidget(clearSearchButton)
        filterLayout.addWidget(self.hideByCustomFiltersButton)
        filterLayout.addWidget(self.unhideByCustomFiltersButton)
        filterLayout.addWidget(self.hideBySelectedButton)
        filterLayout.addWidget(self.showAllButton)

        self._mainLayout.addLayout(filterLayout)
        self._mainLayout.addWidget(self._listWidget)

    def _updateFilter(self, textString):
        count = self._listWidget.count()
        for x in range(count):
            listWidgetItem = self._listWidget.item(x)
            if not textString in listWidgetItem.text():
                listWidgetItem.setHidden(True)
            else:
                listWidgetItem.setHidden(False)

    def __clearSearch(self):
        self._filterInput.setText("")

    def __hideDefaults(self):
        defaultsList = ("message", "publish")

        count = self._listWidget.count()
        for x in range(count):
            listWidgetItem = self._listWidget.item(x)
            if listWidgetItem.text() in defaultsList:
                listWidgetItem.setHidden(True)
            else:
                listWidgetItem.setHidden(False)

        self.hideByCustomFiltersButton.setHidden(True)
        self.unhideByCustomFiltersButton.setHidden(False)

    def __unhideDefaults(self):
        count = self._listWidget.count()
        for x in range(count):
            self._listWidget.item(x).setHidden(False)

        self.hideBySelectedButton.setHidden(False)
        self.showAllButton.setHidden(True)

    def __hideSelected(self):
        count = self._listWidget.count()
        for x in range(count):
            if not self._listWidget.item(x).isSelected():
                self._listWidget.item(x).setHidden(True)

        self.hideBySelectedButton.setHidden(True)
        self.showAllButton.setHidden(False)

    def __showAll(self):
        count = self._listWidget.count()
        for x in range(count):
            self._listWidget.item(x).setHidden(False)

        self.hideBySelectedButton.setHidden(False)
        self.showAllButton.setHidden(True)

    def setSelectionMode(self, selectionMode):
        """convience pass through direct to listWidget"""
        self._listWidget.setSelectionMode(selectionMode)

    # ListWidget pass through
    def findItems(self, name, filter=QtCore.Qt.MatchExactly):
        """convience pass through direct to listWidget"""
        return self._listWidget.findItems(name, filter)

    def addItem(self, item):
        """convience pass through direct to listWidget"""
        return self._listWidget.addItem(item)

    def selectedItems(self):
        """convience pass through direct to listWidget"""
        return self._listWidget.selectedItems()

    def isItemSelected(self, item):
        """convience pass through direct to listWidget"""
        return self._listWidget.isItemSelected(item)

    def setItemSelected(self, item, selected=True):
        """convience pass through direct to listWidget"""
        return self._listWidget.setItemSelected(item, selected)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = ValidityNodeListWidget()
    win.show()
    sys.exit(app.exec_())
