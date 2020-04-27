# coding:utf-8
"""[mconf.py]
Paser node_installation.ini

Raises:
    MCError -- [config format msg]

Returns:
    [bool] -- [true or false]
"""

try:
    import configparser
except Exception:
    from six.moves import configparser
import codecs
from pys.tool import utils
# from pys import path
from pys.log import LOGGER, CONSOLER
from pys.error.exp import MCError


class MchainConf(object):
    """node_installation.ini configuration
    """

    name = 'FISCO Generator'
    group_id = 0
    p2p_listen_port = []
    channel_listen_port = []
    jsonrpc_listen_port = []
    rpc_ip = []
    channel_ip = []
    p2p_ip = []
    peers = []
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

    def get_channel_ip(self):
        """[get channel_ip]

        Returns:
            [string] -- [channel_ip]
        """
        return self.channel_ip

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

    def set_peers(self, _str):
        """[get channel port]

        Returns:
            [string] -- [peers]
        """
        self.peers.append(_str)

    def get_peers(self):
        """[get channel port]

        Returns:
            [string] -- [channel_port]
        """
        return self.peers


def parser(mchain):
    """resolve node_installation.ini

    Arguments:
        mchain {string} -- path of node_installation.ini

    Raises:
        MCError -- exception description
    """

    LOGGER.info('node_installation.ini is %s', mchain)
    # resolve configuration
    if not utils.valid_string(mchain):
        LOGGER.error(
            ' node_installation.ini not invalid path, node_installation.ini is %s', mchain)
        raise MCError(
            ' node_installation.ini not invalid path, node_installation.ini is %s' % mchain)

    # read and parser config file
    config_parser = configparser.ConfigParser(allow_no_value=True)
    try:
        with codecs.open(mchain, 'r', encoding='utf-8') as file_mchain:
            config_parser.readfp(file_mchain)
    except Exception as ini_exp:
        LOGGER.error(
            ' open node_installation.ini file failed, exception is %s', ini_exp)
        raise MCError(
            ' open node_installation.ini file failed, exception is %s' % ini_exp)
    for idx in range(0, 128):
        node_index = ('node{}'.format(idx))
        if config_parser.has_section('group'):
            MchainConf.group_id = config_parser.get('group', 'group_id')
        else:
            LOGGER.error(
                ' invalid node_installation.ini format, group id is %s', MchainConf.group_id)
            raise MCError(
                ' invalid node_installation.ini format, group id is %s' % MchainConf.group_id)

        if config_parser.has_section(node_index):
            p2p_ip = config_parser.get(node_index, 'p2p_ip')
            rpc_ip = config_parser.get(node_index, 'rpc_ip')
            channel_ip = config_parser.get(node_index, 'channel_ip')
            if not utils.valid_ip(p2p_ip):
                LOGGER.error(
                    ' invalid node_installation.ini format, p2p_ip is %s',
                    p2p_ip)
                raise MCError(
                    ' invalid node_installation.ini format, p2p_ip is %s'
                    % p2p_ip)
            # if  rpc_ip == "0.0.0.0" and utils.Status.allow_unsecure_cfg:
            if rpc_ip == "0.0.0.0":
                LOGGER.warning(
                    'Your rpc_ip is %s, this is an unsecurity way', rpc_ip)
                CONSOLER.warning(
                    ' \033[1;31m Your rpc_ip is %s, this is an unsecurity way \033[0m', rpc_ip)
            elif not utils.valid_ip(rpc_ip):
                LOGGER.error(
                    ' invalid node_installation.ini format, rpc_ip is %s',
                    rpc_ip)
                raise MCError(
                    ' invalid node_installation.ini format, rpc_ip is %s'
                    % rpc_ip)
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
            MchainConf.channel_ip.append(channel_ip)
            MchainConf.p2p_listen_port.append(p2p_listen_port)
            MchainConf.jsonrpc_listen_port.append(jsonrpc_listen_port)
            MchainConf.channel_listen_port.append(channel_listen_port)
        else:
            LOGGER.warning(' node%s not existed, break!', idx)
            break
    # if config_parser.has_section('peers'):
    #     for peer in config_parser.items('peers'):
    #         MchainConf.peers.append(peer[1])
    # else:
    #     LOGGER.warning(' section peers not existed!')

    LOGGER.info('group_id is %s', MchainConf.group_id)
    LOGGER.info('p2p_ip is %s', MchainConf.p2p_ip)
    LOGGER.info('rpc_ip is %s', MchainConf.rpc_ip)
    LOGGER.info('channel_ip is %s', MchainConf.channel_ip)
    LOGGER.info('p2p_listen_port is %s', MchainConf.p2p_listen_port)
    LOGGER.info('jsonrpc_listen_port is %s', MchainConf.jsonrpc_listen_port)
    LOGGER.info('channel_listen_port is %s', MchainConf.channel_listen_port)
    LOGGER.info('peers is %s', MchainConf.peers)

    LOGGER.info('node_installation.ini end, result is %s', MchainConf())


def read_peers(data_path):
    """[read peers]

    Arguments:
        data_path {[file]} -- [peers file]
    """
    # read and parser peer file
    try:
        for line in open(data_path):
            peer = line.strip('\n')
            if utils.valid_peer(peer):
                MchainConf.peers.append(peer)
    except Exception as ini_exp:
        LOGGER.error(
            ' open %s file failed, exception is %s', data_path, ini_exp)
        raise MCError(
            ' open %s file failed, exception is %s' % (data_path, ini_exp))
    MchainConf.peers = list(set(MchainConf.peers))
    LOGGER.info('peers is %s', MchainConf.peers)

def default_peers():
    MchainConf.peers = list()
    LOGGER.info('default peers is %s', MchainConf.peers)
