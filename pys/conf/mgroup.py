# coding:utf-8
"""[resolve mgroup.ini]

Raises:
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]

Returns:
    [bool] -- [true or false]
"""

import configparser
import codecs
from pys.tool import utils
# from pys import path
from pys.log import LOGGER
from pys.error.exp import MCError


class MgroupConf(object):
    """mgroup.ini configuration
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
    """resolve mgroup.ini

    Arguments:
        mgroup {string} -- path of mgroup.ini

    Raises:
        MCError -- exception description
    """

    LOGGER.info('mgroup.ini is %s', mgroup)
    # resolve configuration
    if not utils.valid_string(mgroup):
        LOGGER.error(' mgroup.ini not invalid path, mgroup.ini is %s', mgroup)
        raise MCError(
            ' mgroup.ini not invalid path, mgroup.ini is %s' % mgroup)

    # read and parser config file
    config_parser = configparser.ConfigParser()
    try:
        with codecs.open(mgroup, 'r', encoding='utf-8') as file_mchain:
            config_parser.readfp(file_mchain)
    except Exception as ini_exp:
        LOGGER.error(
            ' open mgroup.ini file failed, exception is %s', ini_exp)
        raise MCError(
            ' open mgroup.ini file failed, exception is %s' % ini_exp)

    if config_parser.has_section('group'):
        MgroupConf.group_id = config_parser.get('group', 'group_id')
    else:
        LOGGER.error(
            ' invalid mgroup.ini format, group id is %s', MgroupConf.group_id)
        raise MCError(
            ' invalid mgroup.ini format, group id is %s' % MgroupConf.group_id)

    if not config_parser.has_section('member'):
        LOGGER.error(
            ' invalid mgroup.ini format, member not existed!')
        raise MCError(
            ' invalid mgroup.ini format, member not existed!')

    group_member = config_parser.options('member')

    for members in group_member:
        ctx_mem = config_parser.get('member', members)
        utils.valid_package(ctx_mem)
        MgroupConf.p2p_ip.append(ctx_mem.split(':')[0])
        MgroupConf.p2p_listen_port.append(ctx_mem.split(':')[1])

    LOGGER.info('group_id is %s', MgroupConf.group_id)
    LOGGER.info('p2p_ip is %s', MgroupConf.p2p_ip)
    LOGGER.info('p2p_listen_port is %s', MgroupConf.p2p_listen_port)

    LOGGER.info('mgroup.ini end, result is %s', MgroupConf())
