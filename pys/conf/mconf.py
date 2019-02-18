# coding:utf-8
"""[mconf.py]
Paser mchain.ini

Raises:
    MCError -- [config format msg]

Returns:
    [bool] -- [true or false]
"""

import configparser
import codecs
from pys.tool import utils
# from pys import path
from pys.log import LOGGER
from pys.error.exp import MCError


class MchainConf(object):
    """mchain.ini configuration
    """

    name = 'FISCO Generator'
    group_id = 0
    p2p_listen_port = []
    channel_listen_port = []
    jsonrpc_listen_port = []
    rpc_ip = []
    p2p_ip = []
    # fisco_path = ''

    def __init__(self):
        self.name = 'FISCO BCOS Generator'

    def __repr__(self):
        return 'MchainConf => %s' % (self.name)

    # def set_fisco(path):
    #     MchainConf.fisco_path = path

    # def get_fisco():
    #     return MchainConf.fisco_path

    def get_name(self):
        """[get some name]

        maybe it will usedful not now

        Returns:
            [string] -- [name]
        """
        return self.name

    def get_group_id(self):
        """[get  group_id]


        Returns:
            [string] -- [group_id]
        """
        return self.group_id

    def get_rpc_ip(self):
        """[get rpc_ip]

        Returns:
            [string] -- [rpc_ip]
        """
        return self.rpc_ip

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

    def get_jsonrpc_listen_port(self):
        """[get rpc port]

        Returns:
            [string] -- [rpc_port]
        """
        return self.jsonrpc_listen_port

    def get_channel_listen_port(self):
        """[get channel port]

        Returns:
            [string] -- [channel_port]
        """

        return self.channel_listen_port


def parser(mchain):
    """resolve mchain.ini

    Arguments:
        mchain {string} -- path of mchain.ini

    Raises:
        MCError -- exception description
    """

    LOGGER.info('mchain.ini is %s', mchain)
    # resolve configuration
    if not utils.valid_string(mchain):
        LOGGER.error(' mchain.ini not invalid path, mchain.ini is %s', mchain)
        raise MCError(
            ' mchain.ini not invalid path, mchain.ini is %s' % mchain)

    # read and parser config file
    config_parser = configparser.ConfigParser()
    try:
        with codecs.open(mchain, 'r', encoding='utf-8') as file_mchain:
            config_parser.readfp(file_mchain)
    except Exception as ini_exp:
        LOGGER.error(
            ' open mchain.ini file failed, exception is %s', ini_exp)
        raise MCError(
            ' open mchain.ini file failed, exception is %s' % ini_exp)

    # name = config_parser.get('chain', 'name')
    # if not utils.valid_string(name):
    #     LOGGER.error(
    #         ' invalid mchain.ini format, name empty, agent_name is %s', name)
    #     raise MCError(
    #         ' invalid mchain.ini format, name empty, agent_name is %s' % name)
    # MchainConf.name = name
    for idx in range(0, 128):
        node_index = ('node{}'.format(idx))
        if config_parser.has_section('group'):
            MchainConf.group_id = config_parser.get('group', 'group_id')
        else:
            LOGGER.error(
                ' invalid mchain.ini format, group id is %s', MchainConf.group_id)
            raise MCError(
                ' invalid mchain.ini format, group id is %s' % MchainConf.group_id)

        if config_parser.has_section(node_index):
            p2p_ip = config_parser.get(node_index, 'p2p_ip')
            rpc_ip = config_parser.get(node_index, 'rpc_ip')
            if not utils.valid_ip(rpc_ip):
                LOGGER.error(
                    ' invalid mchain.ini format, rpc_ip is %s, jsonrpc_port is %s',
                    p2p_ip, rpc_ip)
                raise MCError(
                    ' invalid mchain.ini format, p2p_ip is %s, rpc_ip is %s'
                    % (p2p_ip, rpc_ip))
            p2p_listen_port = config_parser.get(node_index, 'p2p_listen_port')
            jsonrpc_listen_port = config_parser.get(
                node_index, 'jsonrpc_listen_port')
            channel_listen_port = config_parser.get(
                node_index, 'channel_listen_port')
            if not (utils.valid_string(p2p_listen_port)
                    and utils.valid_string(jsonrpc_listen_port)
                    and utils.valid_string(channel_listen_port)):
                LOGGER.error(
                    'mchain bad format, p2p_listen_port is %s, '
                    'jsonrpc_port is %s, channel_port is %s',
                    p2p_listen_port, jsonrpc_listen_port, channel_listen_port)
                raise MCError(
                    'mchain bad format, p2p_listen_port is %s, '
                    'jsonrpc_port is %s, channel_port is %s'
                    % (p2p_listen_port, jsonrpc_listen_port, channel_listen_port))
            MchainConf.p2p_ip.append(p2p_ip)
            MchainConf.rpc_ip.append(rpc_ip)
            MchainConf.p2p_listen_port.append(p2p_listen_port)
            MchainConf.jsonrpc_listen_port.append(jsonrpc_listen_port)
            MchainConf.channel_listen_port.append(channel_listen_port)
        else:
            LOGGER.warning(' node%s not existed, break!', idx)
            break

    LOGGER.info('group_id is %s', MchainConf.group_id)
    LOGGER.info('p2p_ip is %s', MchainConf.p2p_ip)
    LOGGER.info('rpc_ip is %s', MchainConf.rpc_ip)
    LOGGER.info('p2p_listen_port is %s', MchainConf.p2p_listen_port)
    LOGGER.info('jsonrpc_listen_port is %s', MchainConf.jsonrpc_listen_port)
    LOGGER.info('channel_listen_port is %s', MchainConf.channel_listen_port)

    LOGGER.info('mchain.ini end, result is %s', MchainConf())
