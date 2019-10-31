import simplejson as json
import logging

logger = logging.getLogger(__name__)


def read(filepath):
    """

    :param filepath: `str`
    :return: `dict`
    """
    logger.info("Reading data from %s" % filepath)
    with open(filepath, "r") as f:
        data = json.load(f)

        return data


def write(filepath, data):
    """

    :param filepath: `str`
    :param data: `dict`
    :return: `bool`
    """
    logger.info("Writing data to %s" % filepath)
    with open(filepath, "w") as outfile:
        outfile.write(json.dumps(data, sort_keys=True))

    logger.info("Wrote date to %s" % filepath)
