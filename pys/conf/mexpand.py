# coding:utf-8
"""[mexpand.py]
Paser mexpand.ini

Raises:
    MCError -- [config format msg]

Returns:
    [bool] -- [true or false]
"""
import configparser
import codecs
from pys.tool import utils
from pys.log import LOGGER
from pys.error.exp import MCError


class MexpandConf(object):
    """mexpand.ini configuration
    """

    name = 'FISCO Generator'
    group_id = 0
    p2p_listen_port = []
    channel_listen_port = []
    jsonrpc_listen_port = []
    rpc_ip = []
    p2p_ip = []
    members = []

    def __init__(self):
        self.name = 'FISCO Generator'

    def __repr__(self):
        return 'MexpandConf %s' % (self.name)

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

    def get_listen_port(self):
        """[get listen port]

        Returns:
            [string] -- [listenning_port]
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

    def get_members(self):
        """[get channel port]

        Returns:
            [string] -- [channel_port]
        """
        return self.members


def parser(mexpand):
    """resolve mexpand.ini

    Arguments:
        mexpand {string} -- path of mexpand.ini

    Raises:
        MCError -- exception description
    """

    LOGGER.info('mexpand.ini is %s', mexpand)
    # resolve configuration
    if not utils.valid_string(mexpand):
        LOGGER.error(
            ' mexpand.ini not invalid path, mexpand.ini is %s', mexpand)
        raise MCError(
            ' mexpand.ini not invalid path, mexpand.ini is %s' % mexpand)

    # read and parser config file
     # read and parser config file
    config_parser = configparser.ConfigParser()
    try:
        with codecs.open(mexpand, 'r', encoding='utf-8') as file_mexpand:
            config_parser.readfp(file_mexpand)
    except Exception as ini_exp:
        LOGGER.error(
            ' open mexpand.ini file failed, exception is %s', ini_exp)
        raise MCError(
            ' open mexpand.ini file failed, exception is %s' % ini_exp)

    # name = config_parser.get('chain', 'name')
    # if not utils.valid_string(name):
    #     LOGGER.error(
    #         ' invalid mexpand.ini format, name empty, agent_name is %s', name)
    #     raise MCError(
    #         ' invalid mexpand.ini format, name empty, agent_name is %s' % name)
    # mexpandConf.name = name
    for idx in range(0, 128):
        node_index = ('node{}'.format(idx))
        if config_parser.has_section('group'):
            MexpandConf.group_id = config_parser.get('group', 'group_id')
        else:
            LOGGER.error(
                ' invalid mchain.ini format, group id is %s', MexpandConf.group_id)
            raise MCError(
                ' invalid mchain.ini format, group id is %s' % MexpandConf.group_id)
        if config_parser.has_section(node_index):
            p2p_ip = config_parser.get(node_index, 'p2p_ip')
            rpc_ip = config_parser.get(node_index, 'rpc_ip')
            if not (utils.valid_ip(p2p_ip) and utils.valid_ip(rpc_ip)):
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
            MexpandConf.p2p_ip.append(p2p_ip)
            MexpandConf.rpc_ip.append(rpc_ip)
            MexpandConf.p2p_listen_port.append(p2p_listen_port)
            MexpandConf.jsonrpc_listen_port.append(jsonrpc_listen_port)
            MexpandConf.channel_listen_port.append(channel_listen_port)
        else:
            LOGGER.warning(' node%s not existed, break!', idx)
            break
    if config_parser.has_section('members'):
        for member in config_parser.items('members'):
            MexpandConf.members.append(member[1])
    else:
        LOGGER.error(' section members not existed!')
        raise MCError(' section members not existed!')

    LOGGER.info('group_id is %s', MexpandConf.group_id)
    LOGGER.info('p2p_ip is %s', MexpandConf.p2p_ip)
    LOGGER.info('rpc_ip is %s', MexpandConf.rpc_ip)
    LOGGER.info('p2p_listen_port is %s', MexpandConf.p2p_listen_port)
    LOGGER.info('jsonrpc_listen_port is %s', MexpandConf.jsonrpc_listen_port)
    LOGGER.info('channel_listen_port is %s', MexpandConf.channel_listen_port)
    LOGGER.info('channel_listen_port is %s', MexpandConf.channel_listen_port)
    LOGGER.info('members is %s', MexpandConf.members)

    LOGGER.info('mchain.ini end, result is %s', MexpandConf())
