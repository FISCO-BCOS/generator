"""[--expand]
"""

from pys.tool import utils
from pys.build import config
from pys import path


def expand(cfg_path, data_path):
    """[--expand]

    Keyword Arguments:
        meta {[type]} -- [description]
        data {[type]} -- [description] (default: {path.get_path()+'/data/expand'})
    """
    utils.file_must_exists('{}/meta/fisco-bcos'.format(path.get_path()))
    utils.file_must_exists('{}/meta/ca.crt'.format(path.get_path()))
    utils.file_must_exists('{}/config.ini'.format(cfg_path))
    utils.dir_must_not_exists(data_path)
    config.expand_config_ini(cfg_path, data_path)
