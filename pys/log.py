# coding:utf-8
"""[pys.log]
"""

import logging
import logging.config

from pys import path

# logging init
logging.config.fileConfig('{}/conf/logging.conf'.format(path.get_path()))
LOGGER = logging.getLogger('instance')
CONSOLER = logging.getLogger('console')


def console_error(message):
    """[print LOGGER]

    Arguments:
        message {[string]} -- [msg of LOGGER]
    """

    CONSOLER.error(' \033[1;31m %s \033[0m', message)


def console_print(message):
    """[print LOGGER]

    Arguments:
        message {[string]} -- [msg of LOGGER]
    """

    CONSOLER.info(' \033[1;32m %s \033[0m', message)
