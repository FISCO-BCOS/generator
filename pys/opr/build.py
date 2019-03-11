"""[--build]
"""

from pys.build import config
from pys.tool import utils
from pys import path


def build(data_path):
    """[--build]
    """
    utils.file_must_exists('{}/meta/fisco-bcos'.format(path.get_path()))
    utils.file_must_exists('{}/meta/ca.crt'.format(path.get_path()))
    config.build_config_ini(data_path)
