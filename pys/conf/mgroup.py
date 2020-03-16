# coding:utf-8
"""[resolve group_genesis.ini]

Raises:
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]

Returns:
    [bool] -- [true or false]
"""
try:
    import configparser
except Exception:
    from six.moves import configparser
import codecs
from pys.tool import utils
from pys.log import LOGGER
from pys.error.exp import MCError


class MgroupConf(object):
    """group_genesis.ini configuration
    """

    name = 'FISCO group'
    group_id = 0
    p2p_listen_port = []
    p2p_ip = []
    # fisco_path = ''

    def __init__(self):
        self.name = 'FISCO BCOS group'

    def __repr__(self):
        return 'MchainConf => %s' % (self.name)

    def get_group_id(self):
        """[get  group_id]


        Returns:
            [string] -- [group_id]
        """
        return self.group_id

    def get_p2p_ip(self):
        """[get p2p_ip]

        Returns:
            [string] -- [p2p_ip]
        """
        return self.p2p_ip

    def get_listen_port(self):
        """[get listen port]

        Returns:
            [string] -- [p2p_listen_port]
        """
        return self.p2p_listen_port


def parser(mgroup):
    """resolve group_genesis.ini

    Arguments:
        mgroup {string} -- path of group_genesis.ini

    Raises:
        MCError -- exception description
    """

    LOGGER.info('group_genesis.ini is %s', mgroup)
    # resolve configuration
    if not utils.valid_string(mgroup):
        LOGGER.error(
            ' group_genesis.ini not invalid path, group_genesis.ini is %s', mgroup)
        raise MCError(
            ' group_genesis.ini not invalid path, group_genesis.ini is %s' % mgroup)

    # read and parser config file
    config_parser = configparser.ConfigParser(allow_no_value=True)
    try:
        with codecs.open(mgroup, 'r', encoding='utf-8') as file_mchain:
            config_parser.readfp(file_mchain)
    except Exception as ini_exp:
        LOGGER.error(
            ' open group_genesis.ini file failed, exception is %s', ini_exp)
        raise MCError(
            ' open group_genesis.ini file failed, exception is %s' % ini_exp)

    if config_parser.has_section('group'):
        MgroupConf.group_id = config_parser.get('group', 'group_id')
    else:
        LOGGER.error(
            ' invalid group_genesis.ini format, group id is %s', MgroupConf.group_id)
        raise MCError(
            ' invalid group_genesis.ini format, group id is %s' % MgroupConf.group_id)

    if not config_parser.has_section('nodes'):
        LOGGER.error(
            ' invalid group_genesis.ini format, nodes not existed!')
        raise MCError(
            ' invalid group_genesis.ini format, nodes not existed!')

    group_nodes = config_parser.options('nodes')

    for node in group_nodes:
        p2p_section = config_parser.get('nodes', node)
        utils.valid_package(p2p_section)
        MgroupConf.p2p_ip.append(p2p_section.split(':')[0])
        MgroupConf.p2p_listen_port.append(p2p_section.split(':')[1])

    LOGGER.info('group_id is %s', MgroupConf.group_id)
    LOGGER.info('p2p_ip is %s', MgroupConf.p2p_ip)
    LOGGER.info('p2p_listen_port is %s', MgroupConf.p2p_listen_port)

    LOGGER.info('group_genesis.ini end, result is %s', MgroupConf())
