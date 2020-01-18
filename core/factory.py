#  Copyright (c) 2020.  James Dunlop
import logging
from core import validator as c_validator
import inside as c_inside
if c_inside.insideMaya():
    from core.maya import validation as cm_mayaValidation

logger = logging.getLogger(__name__)


def createValidator(name, nameSpace="", data=None):
    # type: (str, dict) -> Validator
    """
    Args:
        name: The name for the validator. Eg: MyCat
        data: if supplied will create from data instead
    """
    if data is None:
        validator = c_validator.Validator(name=name, nameSpace=nameSpace)
    else:
        validator = c_validator.Validator.fromData(name=name, data=data)

    if c_inside.insideMaya():  # pragma: no cover
        validator.validate.connect(cm_mayaValidation.validateValidatorSourceNodes)
        validator.repair.connect(cm_mayaValidation.repairValidatorSourceNodes)

    else:  # pragma: no cover
        try:
            msg = lambda x: logger.info(x)
            validator.validate.connect(msg("No stand alone validation is possible!!"))
        except RuntimeError:
            pass

    return validator
