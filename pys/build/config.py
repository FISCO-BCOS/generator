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
try:
    import configparser
except Exception:
    from six.moves import configparser
import codecs
from pys.tool import utils
from pys import path
from pys.log import LOGGER, CONSOLER
from pys.error.exp import MCError
from pys.conf import mconf
import toml


def build_package_only(_data_dir):
    """[-- build create config_ini]

    Keyword Arguments:
        _meta_dir {[PATH]} -- [input dir] (default: {meta})
        _data_dir {[PATH]} -- [output dir] (default: {data})

    Raises:
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
        MCError -- [description]
    """

    LOGGER.info("build_package_only start ")
    p2p_listen_port = mconf.MchainConf.p2p_listen_port
    jsonrpc_listen_port = mconf.MchainConf.jsonrpc_listen_port
    channel_listen_port = mconf.MchainConf.channel_listen_port
    p2p_ip = mconf.MchainConf.p2p_ip
    rpc_ip = mconf.MchainConf.rpc_ip
    channel_ip = mconf.MchainConf.channel_ip
    peers = mconf.MchainConf.peers
    meta_dir = '{}/meta'.format(path.get_path())
    conf_dir = meta_dir
    package_dir = _data_dir
    gm_opr = utils.Status.gm_option

    if os.path.exists(package_dir):
        LOGGER.error(' %s existed, maybe u had created it!', package_dir)
        raise MCError(' %s existed, maybe u had created it!' % package_dir)
    os.mkdir(package_dir)


    if gm_opr:
        shutil.copy('{}/tpl/config.ini.gm'.format(path.get_path()),
                    '{}/.config.ini'.format(conf_dir))
    else:
        shutil.copy('{}/tpl/config.ini'.format(path.get_path()),
                    '{}/.config.ini'.format(conf_dir))
    if utils.Status.gm_ssl:
        utils.replace('{}/.config.ini'.format(conf_dir),
                  'sm_crypto_channel=false',
                  'sm_crypto_channel=true')
    fin_p2p_ip = []
    if not peers:
        LOGGER.warning('section peers not existed!')
        CONSOLER.warn('section peers not existed!')
    else:
        for _, peer in enumerate(peers):
            fin_p2p_ip.append(peer)
    # init config.ini & node package
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      package_dir, node_ip, p2p_listen_port[my_node_index])
        node_dir = '{}/node_{}_{}'.format(package_dir,
                                          node_ip, p2p_listen_port[my_node_index])
        os.mkdir(node_dir)
        os.mkdir('{}/scripts'.format(node_dir))
        shutil.copy('{}/tpl/start.sh'.format(path.get_path()),
                    '{}/start.sh'.format(node_dir))
        shutil.copy('{}/tpl/stop.sh'.format(path.get_path()),
                    '{}/stop.sh'.format(node_dir))
        shutil.copy('{}/tpl/load_new_groups.sh'.format(path.get_path()),
                    '{}/scripts/load_new_groups.sh'.format(node_dir))
        shutil.copy('{}/tpl/reload_whitelist.sh'.format(path.get_path()),
                    '{}/scripts/reload_whitelist.sh'.format(node_dir))
        shutil.copy('{}/fisco-bcos'.format(meta_dir),
                    '{}/fisco-bcos'.format(node_dir))

        os.mkdir('{}/conf'.format(node_dir))
        try:
            # cp config.ini
            shutil.copy('{}/.config.ini'.format(conf_dir),
                        '{}/config.ini'.format(node_dir))
        except Exception as build_exp:
            LOGGER.error(' exception is %s', build_exp)
            utils.delete_data(package_dir)
            raise MCError(' exception is %s' % build_exp)
        node_cfg = configparser.ConfigParser(allow_no_value=True)
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
        if len(rpc_ip) > my_node_index:
            node_cfg.set("rpc", "jsonrpc_listen_ip", rpc_ip[my_node_index])
        else:
            node_cfg.set("rpc", "jsonrpc_listen_ip", "127.0.0.1")

        if len(channel_ip) > my_node_index:
            node_cfg.set("rpc", "channel_listen_ip", channel_ip[my_node_index])
        else:
            node_cfg.set("rpc", "channel_listen_ip", "0.0.0.0")

        node_cfg.set("rpc", "channel_listen_port",
                     channel_listen_port[my_node_index])
        node_cfg.set("rpc", "jsonrpc_listen_port",
                     jsonrpc_listen_port[my_node_index])
        node_cfg.set("p2p", "listen_port", p2p_listen_port[my_node_index])
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
    config_file.close()
    # set p2p ip in config.ini
    for my_node_index, ip_item in enumerate(p2p_ip):
        node_cfg = configparser.ConfigParser(allow_no_value=True)
        if not utils.valid_ip(ip_item):
            LOGGER.error(
                ' init config.ini file failed, found ip => %s', ip_item)
            utils.delete_data(package_dir)
            raise MCError(
                ' init config.ini file failed, found ip => %s' % ip_item)
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
        # write p2pip:port into config.ini
        for ip_idx, set_item in enumerate(p2p_ip):
            fin_p2p_ip.append("{}:{}".format(
                set_item, p2p_listen_port[ip_idx]))
        fin_p2p_ip = list(set(fin_p2p_ip))
        for index, p2p_section in enumerate(fin_p2p_ip):
            node_cfg.set("p2p", "node.{}".format(index),
                         '{}'.format(p2p_section))
            node_cfg.set('certificate_whitelist',
                         '; cal.0 should be nodeid, nodeid\'s length is 128')
            node_cfg.set('certificate_whitelist', ';cal.0=')
            node_cfg.set('certificate_blacklist',
                         '; crl.0 should be nodeid, nodeid\'s length is 128')
            node_cfg.set('certificate_blacklist', ';crl.0=')
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
    os.mkdir(package_dir + '/scripts/')
    shutil.copy('{}/scripts/install.sh'.format(path.get_path()),
                package_dir + '/scripts/')
    shutil.copy('{}/scripts/pack.sh'.format(path.get_path()),
                package_dir + '/scripts/')
    shutil.copy('{}/tpl/start_all.sh'.format(path.get_path()), package_dir)
    shutil.copy('{}/tpl/stop_all.sh'.format(path.get_path()), package_dir)
    shutil.copytree('{}/scripts/monitor'.format((path.get_path())),
                    '{}/monitor'.format(package_dir))
    LOGGER.info("build_package_only end!")


def build_config_ini(_data_dir):
    """[-- build create config_ini]

    Keyword Arguments:
        _meta_dir {[PATH]} -- [input dir] (default: {meta})
        _data_dir {[PATH]} -- [output dir] (default: {data})

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
    channel_ip = mconf.MchainConf.channel_ip
    peers = mconf.MchainConf.peers
    meta_dir = '{}/meta'.format(path.get_path())
    conf_dir = meta_dir
    package_dir = _data_dir
    gm_opr = utils.Status.gm_option
    group_id = mconf.MchainConf.group_id

    utils.file_must_exists('{}/group.{}.genesis'.format(meta_dir, group_id))

    if os.path.exists(package_dir):
        LOGGER.error(' %s existed, maybe u had created it!', package_dir)
        raise MCError(' %s existed, maybe u had created it!' % package_dir)
    os.mkdir(package_dir)

    if gm_opr:
        shutil.copy('{}/tpl/config.ini.gm'.format(path.get_path()),
                    '{}/.config.ini'.format(conf_dir))
    else:
        shutil.copy('{}/tpl/config.ini'.format(path.get_path()),
                    '{}/.config.ini'.format(conf_dir))
    if utils.Status.gm_ssl:
        utils.replace('{}/.config.ini'.format(conf_dir),
                  'sm_crypto_channel=false',
                  'sm_crypto_channel=true')
    fin_p2p_ip = []
    if not peers:
        LOGGER.warning('section peers not existed!')
        CONSOLER.warn('section peers not existed!')
    else:
        for _, peer in enumerate(peers):
            fin_p2p_ip.append(peer)
    # init config.ini & node package
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        try:
            if utils.Status.gm_option:
                utils.file_must_exists('{}/gmcert_{}_{}.crt'.format(conf_dir,
                                                                    node_ip,
                                                                    p2p_listen_port[my_node_index]))
            else:
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
        os.mkdir('{}/scripts'.format(node_dir))
        shutil.copy('{}/tpl/start.sh'.format(path.get_path()),
                    '{}/start.sh'.format(node_dir))
        shutil.copy('{}/tpl/stop.sh'.format(path.get_path()),
                    '{}/stop.sh'.format(node_dir))
        shutil.copy('{}/tpl/load_new_groups.sh'.format(path.get_path()),
                    '{}/scripts/load_new_groups.sh'.format(node_dir))
        shutil.copy('{}/tpl/reload_whitelist.sh'.format(path.get_path()),
                    '{}/scripts/reload_whitelist.sh'.format(node_dir))
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
                shutil.copyfile('{}/gmca.crt'.format(meta_dir),
                                '{}/conf/gmca.crt'.format(node_dir))
            else:
                get_node_cert('{}/cert_{}_{}.crt'.format(meta_dir, node_ip,
                                                         p2p_listen_port[my_node_index]),
                              '{}/conf/node.crt'.format(node_dir))
                shutil.copyfile('{}/ca.crt'.format(meta_dir),
                                '{}/conf/ca.crt'.format(node_dir))
        except Exception as build_exp:
            LOGGER.error(' get node.crt failed ! exception is %s', build_exp)
            utils.delete_data(package_dir)
            raise MCError(' get node.crt failed! exception is %s' % build_exp)
        node_cfg = configparser.ConfigParser(allow_no_value=True)
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
        if len(rpc_ip) > my_node_index:
            node_cfg.set("rpc", "jsonrpc_listen_ip", rpc_ip[my_node_index])
        else:
            node_cfg.set("rpc", "jsonrpc_listen_ip", "127.0.0.1")

        if len(channel_ip) > my_node_index:
            node_cfg.set("rpc", "channel_listen_ip", channel_ip[my_node_index])
        else:
            node_cfg.set("rpc", "channel_listen_ip", "0.0.0.0")
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
        node_cfg = configparser.ConfigParser(allow_no_value=True)
        if not utils.valid_ip(ip_item):
            LOGGER.error(
                ' init config.ini file failed, found ip => %s', ip_item)
            utils.delete_data(package_dir)
            raise MCError(
                ' init config.ini file failed, found ip => %s' % ip_item)
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
        # write p2pip:port into config.ini
        for ip_idx, set_item in enumerate(p2p_ip):
            fin_p2p_ip.append("{}:{}".format(
                set_item, p2p_listen_port[ip_idx]))
        fin_p2p_ip = list(set(fin_p2p_ip))
        for index, p2p_section in enumerate(fin_p2p_ip):
            node_cfg.set("p2p", "node.{}".format(index),
                         '{}'.format(p2p_section))
            node_cfg.set('certificate_whitelist',
                         '; cal.0 should be nodeid, nodeid\'s length is 128')
            node_cfg.set('certificate_whitelist', ';cal.0=')
            node_cfg.set('certificate_blacklist',
                         '; crl.0 should be nodeid, nodeid\'s length is 128')
            node_cfg.set('certificate_blacklist', ';crl.0=')
        with open('{}/config.ini'.format(node_dir), 'w') as config_file:
            node_cfg.write(config_file)
    os.mkdir(package_dir + '/scripts/')
    shutil.copy('{}/scripts/install.sh'.format(path.get_path()),
                package_dir + '/scripts/')
    shutil.copy('{}/scripts/pack.sh'.format(path.get_path()),
                package_dir + '/scripts/')
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

    # with open(get_path) as cert_file:
    #     node_crt = cert_file.read()
    #     cert_begin = node_crt.count(
    #         '-----BEGIN CERTIFICATE-----', 0, len(node_crt))
    #     cert_end = node_crt.count(
    #         '-----END CERTIFICATE-----', 0, len(node_crt))
    #     if (cert_begin != 2) or (cert_end != 2):
    #         LOGGER.error(
    #             ' node cert format checked failed! path is %s', get_path)
    #         raise MCError(
    #             ' node cert format checked failed! path is %s' % get_path)
    #     cert_file.close()
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
        if utils.Status.gm_option:
            (status, result) = utils.getstatusoutput('~/.fisco/tassl x509  -text -in {}'
                                                     ' | sed -n "15,20p" |  sed '
                                                     '"s/://g" | sed "s/pub//g" |'
                                                     ' tr "\n" " " | sed "s/ //g"'
                                                     ' cut -c 3-130| cat >{}'
                                                     .format(get_path, send_path))
        else:
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
        if utils.Status.gm_option:
            (status, result) = utils.getstatusoutput('~/.fisco/tassl x509  -text -in {}'
                                                     ' | sed -n "15,20p" |  sed '
                                                     '"s/://g" | sed "s/pub//g" |'
                                                     ' tr "\n" " " | sed "s/ //g"'
                                                     ' | cut -c 3-130'.format(get_path))
            result = result.split('\n')[0]
        else:
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


def get_nodeid_str_from_nodeid(get_path):
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
        (status, result) = utils.getstatusoutput(
            'cat {} | head -n 1'.format(get_path))
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
    p2p_cfg = configparser.ConfigParser(allow_no_value=True)
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
    p2p_cfg.set('certificate_whitelist',
                '; cal.0 should be nodeid, nodeid\'s length is 128')
    p2p_cfg.set('certificate_whitelist', ';cal.0=')
    p2p_cfg.set('certificate_blacklist',
                '; crl.0 should be nodeid, nodeid\'s length is 128')
    p2p_cfg.set('certificate_blacklist', ';crl.0=')
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
    p2p_cfg = configparser.ConfigParser(allow_no_value=True)
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
    p2p_cfg.set('certificate_whitelist',
                '; cal.0 should be nodeid, nodeid\'s length is 128')
    p2p_cfg.set('certificate_whitelist', ';cal.0=')
    p2p_cfg.set('certificate_blacklist',
                '; crl.0 should be nodeid, nodeid\'s length is 128')
    p2p_cfg.set('certificate_blacklist', ';crl.0=')
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
            ' add peers %s file failed, exception is %s', data_path, ini_exp)
        raise MCError(
            ' add peers %s file failed, exception is %s' % (data_path, ini_exp))
    LOGGER.info('merge peers is %s', p2p_list)
    p2p_list = list(set(p2p_list))
    node_name = os.path.basename(os.path.normpath(_node))
    if utils.valid_node_dir(node_name):
        utils.file_must_exists('{}/config.ini'.format(_node))
        merge_cfg(p2p_list, '{}/config.ini'.format(_node))
    else:
        node_send = utils.get_all_nodes_dir(_node)
        for node_file in node_send:
            utils.file_must_exists('{}/config.ini'.format(node_file))
            merge_cfg(p2p_list, '{}/config.ini'.format(node_file))


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
    node_name = os.path.basename(os.path.normpath(_node))
    if utils.valid_node_dir(node_name):
        utils.file_must_not_exists('{}/conf/{}'.format(_node, file_name))
        shutil.copyfile(data_path, '{}/conf/{}'.format(_node, file_name))
        shutil.copyfile('{}/tpl/group.i.ini'.format(path.get_path()),
                        '{}/conf/group.{}.ini'.format(_node, group_id))
    else:
        node_send = utils.get_all_nodes_dir(_node)
        for node_file in node_send:
            utils.file_must_not_exists(
                '{}/conf/{}'.format(node_file, file_name))
            shutil.copyfile(
                data_path, '{}/conf/{}'.format(node_file, file_name))
            shutil.copyfile('{}/tpl/group.i.ini'.format(path.get_path()),
                            '{}/conf/group.{}.ini'.format(node_file, group_id))


def config_console_toml_file(_file):
    """
    config config.toml of the console
    """
    utils.file_must_exists(_file)
    # Note: the default ip the console connects to is 127.0.0.1
    rpc_ip = mconf.MchainConf.rpc_ip
    channel_listen_port = mconf.MchainConf.channel_listen_port

    with open(_file, mode='rb') as fp:
        content = fp.read()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
    config = toml.loads(content.decode('utf8'))
    for ip_idx, rpc_get in enumerate(rpc_ip):
        config["network"]["peers"][ip_idx] = "{}:{}".format(
            rpc_get, channel_listen_port[ip_idx])
    CONSOLER.info("configure the channel connections to %s",
                  config["network"]["peers"])
    with open(_file, 'w') as fd:
        toml.dump(config, fd)
    CONSOLER.info("config_console_toml_file success")


def get_console_file(_file):
    """[get console file]

    Arguments:
        _file {[type]} -- [description]
    """
    data = _file
    utils.file_must_exists(data)
    # Note: the default ip the console connects to is 127.0.0.1
    rpc_ip = mconf.MchainConf.rpc_ip
    channel_listen_port = mconf.MchainConf.channel_listen_port
    channel_addr = []
    group_id = mconf.MchainConf.group_id
    utils.replace(data,
                  '"group1',
                  '"group{}'.format(group_id))
    utils.replace(data,
                  'name="groupId" value="1"',
                  'name="groupId" value="{}"'.format(group_id))
    for ip_idx, rpc_get in enumerate(rpc_ip):
        channel_addr.append('{}:{}'.format(
            rpc_get, channel_listen_port[ip_idx]))
    cmd = "cat {} | grep -n connectionsStr | awk '{{print $1}}'".format(data)
    (status, result) = utils.getstatusoutput(cmd)
    result = result.strip('\n').strip(':')
    if bool(status):
        LOGGER.error(
            ' append console channel_addr failed, result is %s.', result)
        raise MCError(
            ' append console channel_addr failed, result is %s.' % result)
    line_num = int(result) + 1
    for channel in channel_addr:
        (status, result) \
            = utils.getstatusoutput('sed -i "{} a'
                                    '<value>{}</value>" {}'
                                    .format(line_num, channel, data))
        line_num = line_num + 1
    CONSOLER.info('get console file end')
