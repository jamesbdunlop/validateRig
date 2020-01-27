#  Copyright (c) 2020.  James Dunlop
import logging
from validateRig.const import constants as vrconst_constants
from validateRig.uiElements.trees import validationTreeWidget as vruit_validationTreeWidget
from validateRig.uiElements.trees.treeWidgetItems import factory as cuiettwi_factory
from validateRig.api import vrigCoreApi as vrapi_core

logger = logging.getLogger(__name__)
reload(vruit_validationTreeWidget)


def getValidationTreeWidget(validator, parent):
    # type: (Validator, QtWidgets.QWidget) -> QtWidgets.QTreeWidget
    """
    Args:
        validator: The validator to be used by the treeWidget
        parent: QTWidget for the treeWidget
    """
    treeWidget = vruit_validationTreeWidget.ValidationTreeWidget(validator, parent)
    treeWidget.updateNode.connect(vrapi_core.updateNodeValuesFromDCC)

    for sourceNode in validator.iterSourceNodes():
        sourceNodeTreeWItm = cuiettwi_factory.treeWidgetItemFromNode(node=sourceNode)
        treeWidget.addTopLevelItem(sourceNodeTreeWItm)
        vruit_validationTreeWidget.ValidationTreeWidget.addValidityNodesToTreeWidgetItem(sourceNode, sourceNodeTreeWItm)
        # Crashes maya
        # cuiettwi_factory.setSourceNodeItemWidgetsFromNode(
        #     node=sourceNode, treewidget=treeWidget, twi=sourceNodeTreeWItm
        # )

    treeWidget.resizeColumnToContents(vrconst_constants.SRC_NODENAME_COLUMN)
    treeWidget.resizeColumnToContents(vrconst_constants.DEST_NODENAME_COLUMN)

    return treeWidget

