#  Copyright (c) 2020.  James Dunlop
import logging
from core import validator as c_validator
from core import inside as c_inside
from core import mayaValidation as c_mayaValidation

logger = logging.getLogger(__name__)


def createValidator(name, data=None):
    # type: (str, dict) -> Validator
    """
    Args:
        name: The name for the validator. Eg: MyCat
        data: if supplied will create from data instead
    """
    if data is None:
        validator = c_validator.Validator(name=name)
    else:
        validator = c_validator.Validator.fromData(name, data)

    if c_inside.insideMaya():  # pragma: no cover
        validator.validate.connect(c_mayaValidation.validateValidatorSourceNodes)
        validator.repair.connect(c_mayaValidation.repairValidatorSourceNodes)

    else:  # pragma: no cover
        msg = lambda x: logger.info(x)
        validator.validate.connect(msg("No stand alone validation is possible!!"))

    return validator
