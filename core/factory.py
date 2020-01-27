#  Copyright (c) 2020.  James Dunlop
import logging
from validateRig import insideDCC as vr_insideDCC
from validateRig.core import validator as vrc_validator
if vr_insideDCC.insideMaya():
    import validateRig.core.maya.validation as cm_mayaValidation

logger = logging.getLogger(__name__)


def createValidator(name, nameSpace="", data=None):
    # type: (str, dict) -> Validator
    """
    Args:
        name: The name for the validator. Eg: MyCat
        data: if supplied will create from data instead
    """
    if data is None:
        validator = vrc_validator.Validator(name=name, nameSpace=nameSpace)
    else:
        validator = vrc_validator.Validator.fromData(name=name, data=data)

    if vr_insideDCC.insideMaya():  # pragma: no cover
        validator.validate.connect(cm_mayaValidation.validateValidatorSourceNodes)
        validator.repair.connect(cm_mayaValidation.repairValidatorSourceNodes)

    else:  # pragma: no cover
        try:
            msg = lambda x: logger.debug(x)
            validator.validate.connect(msg("No stand alone validation is possible!!"))
        except RuntimeError:
            pass

    return validator
