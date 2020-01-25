#  Copyright (c) 2020.  James Dunlop
import logging
from validateRig.const import constants as vrc_constants
from validateRig.uiElements.trees import validationTreeWidget as vruit_validationTreeWidget
from validateRig.uiElements.trees.treeWidgetItems import factory as cuitwi_factory
from validateRig.api import vr_core_api

logger = logging.getLogger(__name__)


def getValidationTreeWidget(validator, parent):
    # type: (Validator, QtWidgets.QWidget) -> QtWidgets.QTreeWidget
    """
    Args:
        validator: The validator to be used by the treeWidget
        parent: QTWidget for the treeWidget
    """
    treeWidget = vruit_validationTreeWidget.ValidationTreeWidget(validator, parent)
    treeWidget.updateNode.connect(vr_core_api.updateNodeValuesFromDCC)

    for sourceNode in validator.iterSourceNodes():
        sourceNodeTreeWItm = cuitwi_factory.treeWidgetItemFromNode(node=sourceNode)
        treeWidget.addTopLevelItem(sourceNodeTreeWItm)
        vruit_validationTreeWidget.ValidationTreeWidget.addValidityNodesToTreeWidgetItem(sourceNode, sourceNodeTreeWItm)
        # Crashes maya
        # cuitwi_factory.setSourceNodeItemWidgetsFromNode(
        #     node=sourceNode, treewidget=treeWidget, twi=sourceNodeTreeWItm
        # )

    treeWidget.resizeColumnToContents(vrc_constants.SRC_NODENAME_COLUMN)
    treeWidget.resizeColumnToContents(vrc_constants.DEST_NODENAME_COLUMN)

    return treeWidget

