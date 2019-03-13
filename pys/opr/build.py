"""[--build]
"""

from pys.build import config
from pys.tool import utils
from pys import path
from pys.conf import mconf
from pys.opr import opr_cert


def build(peer_path, data_path):
    """[--build]
    """
    utils.file_must_exists('{}/meta/fisco-bcos'.format(path.get_path()))
    utils.file_must_exists('{}/meta/ca.crt'.format(path.get_path()))
    utils.file_must_exists(peer_path)
    mconf.read_peers(peer_path)
    config.build_config_ini(data_path)
    opr_cert.deploy_key('{}/meta'.format(path.get_path()), data_path)
    