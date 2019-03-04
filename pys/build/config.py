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
from pys.conf import mexpand
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
            [string] -- [group_id]
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

    meta_dir = '{}/meta'.format(path.get_path())
    package_dir = _data_dir
    gm_opr = get_status()

    if os.path.exists(package_dir):
        LOGGER.error(' ./data existed, maybe u had created it!')
        raise MCError(' ./data existed, maybe u had created it!')
    os.mkdir(package_dir)

    # init config.ini & node package
    my_node_index = 0
    for node_ip in p2p_ip:
        LOGGER.info("p2p_ip -> %s", node_ip)
        LOGGER.info(" need %s config.ini", len(p2p_ip))
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
                shutil.copy('{}/tpl/config.ini'.format(path.get_path()),
                            '{}/config.ini'.format(node_dir))
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
        node_cfg.set("p2p", "listen_ip", p2p_ip[my_node_index])
        node_cfg.set("p2p", "listen_port", p2p_listen_port[my_node_index])
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
        my_node_index = my_node_index + 1
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
    os.system('cp {}/node_{}_{}/config.ini'
              ' {}/config.ini'.format(package_dir,
                                      p2p_ip[0], p2p_listen_port[0], package_dir))
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


def expand_config_ini(conf_path, data_path='{}/data'.format(path.get_path())):
    """[--expand]

    Arguments:
        conf_path {[PATH]} -- [conf path]

    Keyword Arguments:
        data_path {[PATH]} -- [pkg path] (default: {'{}/data'.format(path.get_path())})

    Raises:
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
    """

    LOGGER.info("expand_config_ini start!")

    p2p_listen_port = mexpand.MexpandConf.p2p_listen_port
    p2p_ip = mexpand.MexpandConf.p2p_ip
    rpc_ip = mexpand.MexpandConf.rpc_ip
    jsonrpc_listen_port = mexpand.MexpandConf.jsonrpc_listen_port
    channel_listen_port = mexpand.MexpandConf.channel_listen_port
    members = mexpand.MexpandConf.members
    group_id = mexpand.MexpandConf.group_id
    gm_opr = get_status()
    conf_dir = conf_path

    meta_dir = path.get_path() + '/meta'
    package_dir = data_path

    # node_id
    if not os.path.exists(meta_dir):
        LOGGER.error(' meta path not existed! path is %s', meta_dir)
        raise MCError(' meta path not existed! path is %s' % meta_dir)
    if not os.path.exists(conf_dir):
        LOGGER.error(' conf path not existed! path is %s', conf_dir)
        raise MCError(' conf path not existed! path is %s' % conf_dir)
    if not os.path.isfile('{}/group.{}.genesis'.format(conf_dir, group_id)):
        LOGGER.error(' file not complete ! need group.%s.genesis',
                     group_id, group_id)
        raise MCError(' file not complete ! need group.%s.genesis' % (
            group_id))

    if os.path.exists(package_dir):
        LOGGER.error(
            ' data path existed! path is %s', package_dir)
        raise MCError(
            ' data path existed! path is %s' % package_dir)
    os.mkdir(package_dir)
    default_cfg = configparser.ConfigParser()
    shutil.copy('{}/tpl/config.ini'.format(path.get_path()),
                            '{}/.config.ini'.format(conf_dir))
    try:
        with codecs.open('{}/.config.ini'.format(conf_dir),
                            'r', encoding='utf-8') as config_file:
            default_cfg.readfp(config_file)
    except Exception as expand_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', expand_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % expand_exp)
    for id, member in enumerate(members):
        default_cfg.set("p2p", "node.{}".format(id),
                        '{}'.format(member))
    with open('{}/.config.ini'.format(conf_dir), 'w') as config_file:
        default_cfg.write(config_file)

    # init config.ini & node package
    my_node_index = 0
    for node_ip in p2p_ip:
        LOGGER.info("p2p_ip -> %s", node_ip)
        LOGGER.info(" need %s config.ini", len(p2p_ip))
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
            shutil.copy('{}/.config.ini'.format(conf_dir),
                        '{}/config.ini'.format(node_dir))
            shutil.copy('{}/group.{}.genesis'.format(conf_dir, group_id),
                        '{}/conf/group.{}.genesis'.format(node_dir, group_id))
            shutil.copy('{}/tpl/group.i.ini'.format(path.get_path()),
                        '{}/conf/group.{}.ini'.format(node_dir, group_id))
            if gm_opr:
                get_node_cert('{}/gmcert_{}_{}.crt'.format(meta_dir, node_ip,
                                                           p2p_listen_port[my_node_index]),
                              '{}/conf/gmnode.crt'.format(node_dir))
                get_nodeid('{}/conf/gmnode.crt'.format(node_dir),
                           '{}/conf/gmnode.nodeid'.format(node_dir))
                os.system(
                    'cp {}/gmca.crt {}/conf/gmca.crt'.format(meta_dir, node_dir))

            else:
                get_node_cert('{}/cert_{}_{}.crt'.format(meta_dir, node_ip,
                                                         p2p_listen_port[my_node_index]),
                              '{}/conf/node.crt'.format(node_dir))
                get_nodeid('{}/conf/node.crt'.format(node_dir),
                           '{}/conf/node.nodeid'.format(node_dir))
                os.system(
                    'cp {}/ca.crt {}/conf/ca.crt'.format(meta_dir, node_dir))

        except Exception as expand_exp:
            LOGGER.error(' get node.crt failed ! exception is %s', expand_exp)
            utils.delete_data(package_dir)
            raise MCError(' get node.crt failed! exception is %s' % expand_exp)
        node_cfg = configparser.ConfigParser()
        try:
            with codecs.open('{}/config.ini'.format(node_dir),
                             'r', encoding='utf-8') as config_file:
                node_cfg.readfp(config_file)
        except Exception as expand_exp:
            LOGGER.error(
                ' open config.ini file failed, exception is %s', expand_exp)
            utils.delete_data(package_dir)
            raise MCError(
                ' open config.ini file failed, exception is %s' % expand_exp)
        node_cfg.set("rpc", "listen_ip", rpc_ip[my_node_index])
        node_cfg.set("rpc", "channel_listen_port",
                     channel_listen_port[my_node_index])
        node_cfg.set("rpc", "jsonrpc_listen_port",
                     jsonrpc_listen_port[my_node_index])
        node_cfg.set("p2p", "listen_ip", p2p_ip[my_node_index])
        node_cfg.set("p2p", "listen_port", p2p_listen_port[my_node_index])
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
        my_node_index = my_node_index + 1
    start_index = len(node_cfg.items('p2p')) - 2
    LOGGER.info("start index is %s!", start_index)
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
        except Exception as expand_exp:
            LOGGER.error(
                ' open config.ini file failed, exception is %s', expand_exp)
            utils.delete_data(package_dir)
            raise MCError(
                ' open config.ini file failed, exception is %s' % expand_exp)
        for ip_idx, set_item in enumerate(p2p_ip):
            node_cfg.set("p2p", "node.{}".format(ip_idx + start_index),
                         '{}:{}'.format(set_item, p2p_listen_port[ip_idx]))
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
    os.system('cp {}/node_{}_{}/config.ini'
              ' {}/config.ini'.format(package_dir,
                                      p2p_ip[0], p2p_listen_port[0], package_dir))
    shutil.copy('{}/tpl/start_all.sh'.format(path.get_path()), package_dir)
    shutil.copy('{}/tpl/stop_all.sh'.format(path.get_path()), package_dir)
    shutil.copytree('{}/scripts/monitor'.format((path.get_path())),
                    '{}/monitor'.format(package_dir))
    LOGGER.info("expand_config_ini end!")


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
    except Exception as expand_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', expand_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % expand_exp)
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
    except Exception as expand_exp:
        LOGGER.error(
            ' open config.ini file failed, exception is %s', expand_exp)
        raise MCError(
            ' open config.ini file failed, exception is %s' % expand_exp)
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
