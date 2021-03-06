#  Copyright (c) 2019.  James Dunlop
import logging
import simplejson as json

logger = logging.getLogger(__name__)


def read(filepath):
    """

    :param filepath: `str`
    :return: `dict`
    """
    logger.debug("Reading data from %s" % filepath)
    with open(filepath, "r") as f:
        data = json.load(f)

        return data


def write(filepath, data):
    """

    :param filepath: `str`
    :param data: `dict`
    :return: `bool`
    """
    logger.debug("Saving data to %s" % filepath)
    with open(filepath, "w") as outfile:
        outfile.write(json.dumps(data, sort_keys=True))

    logger.debug("Successfully saved data to %s" % filepath)
    return True
