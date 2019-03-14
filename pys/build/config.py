"""[paser ini]

Raises:
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]

Returns:
    [bool] -- [true or false]
"""
import os
import shutil
import configparser
import codecs
from pys.tool import utils
from pys import path
from pys.log import LOGGER, CONSOLER
from pys.error.exp import MCError
from pys.conf import mconf


class Status(object):
    """[gm Status]

    Arguments:
        object {[type]} -- [description]
    """

    gm_option = False
    unit_time = False

    def __init__(self):
        """[init]
        """

        self. gm_option = False

    def get_gm_staus(self):
        """[get gm_option]


        Returns:
            [string] -- [gm]
        """
        return self.gm_option

    def get_ut_status(self):
        """[get unit_time]

        Returns:
            [string] -- [rpc_ip]
        """
        return self.unit_time


def set_gm():
    """[set gm]
    """

    Status.gm_option = True


def get_status():
    """[get gm or not]

    Returns:
        [bool] -- [true of false]
    """

    return Status.gm_option


def build_config_ini(_data_dir):
    """[-- build create config_ini]

    Keyword Arguments:
        _meta_dir {[PATH]} -- [input dir] (default: {path.get_path()+'/meta'})
        _data_dir {[PATH]} -- [output dir] (default: {path.get_path()+'/data'})

    Raises:
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
    """

    LOGGER.info("build_config_ini start ")
    p2p_listen_port = mconf.MchainConf.p2p_listen_port
    jsonrpc_listen_port = mconf.MchainConf.jsonrpc_listen_port
    channel_listen_port = mconf.MchainConf.channel_listen_port
    p2p_ip = mconf.MchainConf.p2p_ip
    rpc_ip = mconf.MchainConf.rpc_ip
    peers = mconf.MchainConf.peers
    meta_dir = '{}/meta'.format(path.get_path())
    conf_dir = meta_dir
    package_dir = _data_dir
    gm_opr = get_status()
    group_id = mconf.MchainConf.group_id

    utils.file_must_exists('{}/group.{}.genesis'.format(meta_dir, group_id))

    if os.path.exists(package_dir):
        LOGGER.error(' ./data existed, maybe u had created it!')
        raise MCError(' ./data existed, maybe u had created it!')
    os.mkdir(package_dir)

    default_cfg = configparser.ConfigParser()
    shutil.copy('{}/tpl/config.ini'.format(path.get_path()),
                '{}/.config.ini'.format(conf_dir))
    try:
        with codecs.open('{}/.config.ini'.format(conf_dir),
                         'r', encoding='utf-8') as config_file:
            default_cfg.readfp(config_file)
    except Exception as build_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', build_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % build_exp)
    if not peers:
        LOGGER.warning('section peers not existed!')
        CONSOLER.warn('section peers not existed!')
    else:
        for node_id, peer in enumerate(peers):
            default_cfg.set("p2p", "node.{}".format(node_id + len(p2p_listen_port)),
                            peer)
        with open('{}/.config.ini'.format(conf_dir), 'w') as config_file:
            default_cfg.write(config_file)

    # init config.ini & node package
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        try:
            utils.file_must_exists('{}/cert_{}_{}.crt'.format(conf_dir,
                                                              node_ip,
                                                              p2p_listen_port[my_node_index]))
        except Exception as build_exp:
            LOGGER.error('%s', build_exp)
            raise MCError('%s' % build_exp)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      package_dir, node_ip, p2p_listen_port[my_node_index])
        node_dir = '{}/node_{}_{}'.format(package_dir,
                                          node_ip, p2p_listen_port[my_node_index])
        os.mkdir(node_dir)
        shutil.copy('{}/tpl/start.sh'.format(path.get_path()),
                    '{}/start.sh'.format(node_dir))
        shutil.copy('{}/tpl/stop.sh'.format(path.get_path()),
                    '{}/stop.sh'.format(node_dir))
        shutil.copy('{}/fisco-bcos'.format(meta_dir),
                    '{}/fisco-bcos'.format(node_dir))

        os.mkdir('{}/conf'.format(node_dir))
        try:
            # get node cert
            if gm_opr:
                shutil.copy('{}/tpl/config.ini.gm'.format(path.get_path()),
                            '{}/config.ini'.format(node_dir))
                get_node_cert('{}/gmcert_{}_{}.crt'.format(meta_dir, node_ip,
                                                           p2p_listen_port[my_node_index]),
                              '{}/conf/gmnode.crt'.format(node_dir))
                get_nodeid('{}/conf/gmnode.crt'.format(node_dir),
                           '{}/conf/gmnode.nodeid'.format(node_dir))
                shutil.copyfile('{}/gmca.crt'.format(meta_dir),
                                '{}/conf/gmca.crt'.format(node_dir))
            else:
                shutil.copy('{}/.config.ini'.format(conf_dir),
                            '{}/config.ini'.format(node_dir))
                shutil.copy('{}/group.{}.genesis'.format(conf_dir, group_id),
                            '{}/conf/group.{}.genesis'.format(node_dir, group_id))
                shutil.copy('{}/tpl/group.i.ini'.format(path.get_path()),
                            '{}/conf/group.{}.ini'.format(node_dir, group_id))
                get_node_cert('{}/cert_{}_{}.crt'.format(meta_dir, node_ip,
                                                         p2p_listen_port[my_node_index]),
                              '{}/conf/node.crt'.format(node_dir))
                get_nodeid('{}/conf/node.crt'.format(node_dir),
                           '{}/conf/node.nodeid'.format(node_dir))
                shutil.copyfile('{}/ca.crt'.format(meta_dir),
                                '{}/conf/ca.crt'.format(node_dir))
        except Exception as build_exp:
            LOGGER.error(' get node.crt failed ! exception is %s', build_exp)
            utils.delete_data(package_dir)
            raise MCError(' get node.crt failed! exception is %s' % build_exp)
        node_cfg = configparser.ConfigParser()
        try:
            with codecs.open('{}/config.ini'.format(node_dir),
                             'r', encoding='utf-8') as config_file:
                node_cfg.readfp(config_file)
        except Exception as build_exp:
            LOGGER.error(
                ' open config.ini file failed, exception is %s', build_exp)
            utils.delete_data(package_dir)
            raise MCError(
                ' open config.ini file failed, exception is %s' % build_exp)
        node_cfg.set("rpc", "listen_ip", rpc_ip[my_node_index])
        node_cfg.set("rpc", "channel_listen_port",
                     channel_listen_port[my_node_index])
        node_cfg.set("rpc", "jsonrpc_listen_port",
                     jsonrpc_listen_port[my_node_index])
        # node_cfg.set("p2p", "listen_ip", p2p_ip[my_node_index])
        node_cfg.set("p2p", "listen_port", p2p_listen_port[my_node_index])
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
    config_file.close()
    # set p2p ip in config.ini
    for my_node_index, ip_item in enumerate(p2p_ip):
        node_cfg = configparser.ConfigParser()
        node_dir = '{}/node_{}_{}'.format(package_dir,
                                          ip_item, p2p_listen_port[my_node_index])
        try:
            with codecs.open('{}/config.ini'.format(node_dir),
                             'r', encoding='utf-8') as config_file:
                node_cfg.readfp(config_file)
        except Exception as build_exp:
            LOGGER.error(
                ' open config.ini file failed, exception is %s', build_exp)
            utils.delete_data(package_dir)
            raise MCError(
                ' open config.ini file failed, exception is %s' % build_exp)
        for ip_idx, set_item in enumerate(p2p_ip):
            node_cfg.set("p2p", "node.{}".format(ip_idx),
                         '{}:{}'.format(set_item, p2p_listen_port[ip_idx]))
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
    # shutil.copy('{}/node_{}_{}/config.ini'.format(package_dir,
    #                                               p2p_ip[0],
    #                                               p2p_listen_port[0]),
    #             '{}/config.ini'.format(package_dir))
    shutil.copy('{}/tpl/start_all.sh'.format(path.get_path()), package_dir)
    shutil.copy('{}/tpl/stop_all.sh'.format(path.get_path()), package_dir)
    shutil.copytree('{}/scripts/monitor'.format((path.get_path())),
                    '{}/monitor'.format(package_dir))
    LOGGER.info("build_config_ini end!")


def get_node_cert(get_path, send_path):
    """[get node crt to conf/]

    Arguments:
        get_path {[PATH]} -- [input file]
        send_path {[PATH]} -- [output file]

    Raises:
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
    """

    LOGGER.info("get node.crt in %s", get_path)
    LOGGER.info("send node.crt in %s", send_path)
    if not os.path.isfile(get_path):
        LOGGER.error(' node cert doesn\'t existed! Need %s', get_path)
        raise MCError(' node cert doesn\'t existed! Need %s' % get_path)
    if os.path.isfile(send_path):
        LOGGER.error(' node.crt existed! path is %s', send_path)
        raise MCError(' node.crt existed! path is %s' % send_path)

    with open(get_path) as cert_file:
        node_crt = cert_file.read()
        cert_begin = node_crt.count(
            '-----BEGIN CERTIFICATE-----', 0, len(node_crt))
        cert_end = node_crt.count(
            '-----END CERTIFICATE-----', 0, len(node_crt))
        if (cert_begin != 2) or (cert_end != 2):
            LOGGER.error(
                ' node cert format checked failed! path is %s', get_path)
            raise MCError(
                ' node cert format checked failed! path is %s' % get_path)
        cert_file.close()
    shutil.copy(get_path, send_path)
    LOGGER.info("get_node_cert success! get path is %s", get_path)
    LOGGER.info("get_node_cert success! send path is %s", send_path)


def get_nodeid(get_path, send_path):
    """[get nodeid into file]

    Arguments:
        get_path {[file]} -- [description]
        send_path {[file]} -- [description]

    Raises:
        MCError -- [description]
    """

    LOGGER.info("get_nodeid start! get path is %s", get_path)
    LOGGER.info("get_nodeid start! send path is %s", send_path)
    if not os.path.isfile(get_path):
        LOGGER.error(' node cert doesn\'t existed! Need %s', get_path)
        raise MCError(' node cert doesn\'t existed! Need %s' % get_path)
    try:
        (status, result) = utils.getstatusoutput('openssl x509  -text -in {}'
                                                 ' | sed -n "15,20p" |  sed "s/://g"'
                                                 ' | tr "\n" " " | sed "s/ //g" |'
                                                 ' cut -c 3-130| cat >{}'
                                                 .format(get_path, send_path))
        if status != 0:
            LOGGER.error(
                ' create nodeid failed! status is %d, output is %s, dir is %s.',
                status, result, get_path)
        LOGGER.info(
            ' create nodeid success! status is %d, output is %s, dir is %s.',
            status, result, get_path)
    except Exception as node_id_exp:
        LOGGER.error(
            ' create nodeid failed! status is %d, output is %s, dir is %s.',
            status, result, get_path)
        raise MCError(' create nodeid failed! excepion is %s.' % node_id_exp)
    LOGGER.info("get_nodeid success! get path is %s", get_path)
    LOGGER.info("get_nodeid success! send path is %s", send_path)


def get_nodeid_str(get_path):
    """[get nodeid string]

    Arguments:
        get_path {[file]} -- [description]

    Raises:
        MCError -- [description]

    Returns:
        [string] -- [nodeid]
    """

    # openssl x509  -text -in ./node.crt |  sed -n '15,20p' |  sed 's/://g' |
    #  tr "\n" " " | sed 's/ //g' | sed 's/pub//g' | cut -c 3-130
    LOGGER.info("get_nodeid start! get path is %s", get_path)
    if not os.path.isfile(get_path):
        LOGGER.error(' node cert doesn\'t existed! Need %s', get_path)
        raise MCError(' node cert doesn\'t existed! Need %s' % get_path)
    try:
        (status, result) = utils.getstatusoutput('openssl x509  -text -in {}'
                                                 ' | sed -n "15,20p" |  sed '
                                                 '"s/://g" | sed "s/pub//g" |'
                                                 ' tr "\n" " " | sed "s/ //g"'
                                                 ' | cut -c 3-130'.format(get_path))

        if status != 0:
            LOGGER.error(
                ' create nodeid failed! status is %d, output is %s, dir is %s.',
                status, result, get_path)
        LOGGER.info(
            ' create nodeid success! status is %d, output is %s, dir is %s.',
            status, result, get_path)
    except Exception as node_id_exp:
        LOGGER.error(
            ' create nodeid failed! status is %d, output is %s, dir is %s.',
            status, result, get_path)
        raise MCError(' create nodeid failed! excepion is %s.' % node_id_exp)
    LOGGER.info("get_nodeid success! get path is %s", get_path)
    return result


def concatenate_cfg(cfg_file, cfg_file_get):
    """[combine two config.ini]

    Arguments:
        cfg_file {[type]} -- [description]
        cfg_file_get {[type]} -- [description]

    Raises:
        MCError -- [description]
    """

    LOGGER.info("concatenate two config.ini now!")
    meta = cfg_file
    data = cfg_file_get
    utils.file_must_exists(meta)
    utils.file_must_exists(data)
    p2p_get = []
    p2p_get_ip = []
    p2p_send = []
    p2p_send_ip = []
    p2p_cfg = configparser.ConfigParser()
    try:
        with codecs.open(meta, 'r', encoding='utf-8') as config_file:
            p2p_cfg.readfp(config_file)
    except Exception as build_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', build_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % build_exp)
    p2p_get = p2p_cfg.items('p2p')
    p2p_get.pop(0)
    p2p_get.pop(0)
    LOGGER.info("get node is %s!", p2p_get)
    for node_tuple in p2p_get:
        p2p_get_ip.append(node_tuple[1])
    LOGGER.info("get node ip is %s!", p2p_get_ip)
    try:
        with codecs.open(data, 'r', encoding='utf-8') as config_file:
            p2p_cfg.readfp(config_file)
    except Exception as build_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', build_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % build_exp)
    p2p_send = p2p_cfg.items('p2p')
    p2p_send.pop(0)
    p2p_send.pop(0)
    LOGGER.info("send node is %s!", p2p_send)
    for node_tuple in p2p_send:
        p2p_send_ip.append(node_tuple[1])
    LOGGER.info("get node ip is %s!", p2p_send_ip)
    p2p_send_ip = list(set(p2p_get_ip + p2p_send_ip))
    LOGGER.info("final node ip is %s!", p2p_send_ip)
    for ip_idx, p2p_ip in enumerate(p2p_send_ip):
        p2p_cfg.set("p2p", "node.{}".format(ip_idx), p2p_ip)
    with open(data, 'w') as config_file:
        p2p_cfg.write(config_file)
    LOGGER.info(
        "concatenate two config.ini now! output => %s/conf/config.ini", data)


def merge_cfg(p2p_list, cfg_file):
    """[combine config.ini]

    Arguments:
        p2p_list {[type]} -- [list]
        cfg_file {[type]} -- [file]

    Raises:
        MCError -- [description]
    """

    LOGGER.info("merge peers to config.ini now!")
    data = cfg_file
    utils.file_must_exists(data)
    p2p_get = p2p_list
    p2p_send = []
    p2p_cfg = configparser.ConfigParser()
    try:
        with codecs.open(data, 'r', encoding='utf-8') as config_file:
            p2p_cfg.readfp(config_file)
    except Exception as build_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', build_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % build_exp)
    if p2p_cfg.has_section('p2p'):
        p2p_send_opt = p2p_cfg.options('p2p')
    else:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', build_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % build_exp)
    for node in p2p_send_opt:
        p2p_section = p2p_cfg.get('p2p', node)
        p2p_send.append(p2p_section)
    p2p_send.pop(0)
    p2p_send.pop(0)
    LOGGER.info("send node is %s!", p2p_send)
    # for node_tuple in p2p_send:
    #     p2p_send.append(node_tuple)
    LOGGER.info("get node ip is %s!", p2p_get)
    p2p_send = list(set(p2p_send + p2p_get))
    LOGGER.info("final node ip is %s!", p2p_send)
    for ip_idx, p2p_ip in enumerate(p2p_send):
        p2p_cfg.set("p2p", "node.{}".format(ip_idx), p2p_ip)
    with open(data, 'w') as config_file:
        p2p_cfg.write(config_file)
    LOGGER.info(
        "concatenate config.ini now! output => %s/conf/config.ini", data)
    return True


def add_peers2cfg(_peers, _node):
    """[summary]

    Arguments:
        _peers {[type]} -- [description]
        _node {[type]} -- [description]
    """
    data_path = _peers
    p2p_list = []
    node_send = []
    utils.file_must_exists(data_path)
    try:
        for line in open(data_path):
            peer = line.strip('\n')
            utils.valid_peer(peer)
            p2p_list.append(peer)
    except Exception as ini_exp:
        LOGGER.error(
            ' open %s file failed, exception is %s', data_path, ini_exp)
        raise MCError(
            ' open %s file failed, exception is %s' % (data_path, ini_exp))
    LOGGER.info('merge peers is %s', p2p_list)
    p2p_list = list(set(p2p_list))
    node_send = utils.get_all_nodes_dir(_node)
    for file in node_send:
        utils.file_must_exists('{}/config.ini'.format(file))
        merge_cfg(p2p_list, '{}/config.ini'.format(file))


def add_group(_group, _node):
    """
    Arguments:
        _group {[type]} -- [description]
        _node {[type]} -- [description]
    """
    data_path = _group
    node_send = []
    utils.file_must_exists(data_path)
    file_name = os.path.basename(data_path)
    group_id = utils.valid_genesis(file_name)
    if group_id == 0:
        raise MCError(' paser %s file failed' % (data_path))
    node_send = utils.get_all_nodes_dir(_node)
    for file in node_send:
        utils.file_must_not_exists('{}/conf/{}'.format(file, file_name))
        shutil.copyfile(data_path, '{}/conf/{}'.format(file, file_name))
        shutil.copyfile('{}/tpl/group.i.ini'.format(path.get_path()),
                        '{}/conf/group.{}.ini'.format(file, group_id))