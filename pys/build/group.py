"""[group.py]


Raises:
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
"""
import os
import shutil
try:
    import configparser
except Exception:
    from six.moves import configparser
from pys import path
from pys.log import LOGGER, CONSOLER
from pys.error.exp import MCError
from pys.conf import mgroup
from pys.build import config
from pys.tool import utils


def create_group_genesis(data_dir='{}/meta'.format(path.get_path())):
    '''
    create group in meta
    '''
    LOGGER.info('create_group_genesis start')
    package_dir = data_dir
    gm_opr = utils.Status.gm_option
    group_id = mgroup.MgroupConf.group_id
    p2p_ip = mgroup.MgroupConf.p2p_ip
    p2p_listen_port = mgroup.MgroupConf.p2p_listen_port
    utils.file_must_not_exists(
        '{}/group.{}.genesis'.format(data_dir, group_id))
    if not os.path.exists(package_dir):
        LOGGER.warning(' %s not existed!', package_dir)
        os.mkdir(data_dir)
    shutil.copy('{}/tpl/group.i.genesis'.format(path.get_path()),
                '{}/group.{}.genesis'.format(package_dir, group_id))
    shutil.copy('{}/tpl/group.i.ini'.format(path.get_path()),
                '{}/group.{}.ini'.format(package_dir, group_id))
    # updates second to ms
    (status, time_stamp) = utils.getstatusoutput('echo $(date +%s"000")')
    if not bool(status):
        CONSOLER.info('generate %s/group.%s.genesis, successful',
                      package_dir, group_id)
    else:
        LOGGER.error(
            ' Generate %s/group.%s.genesis failed! Please check your network.',
            package_dir, group_id)
        raise MCError(
            ' Generate %s/group.%s.genesis failed, timestamp is %s! Please check your network.'
            % (package_dir, group_id, time_stamp))
    # CONSOLER.info('generate %s/group.%s.ini', package_dir, group_id)
    group_cfg = configparser.ConfigParser(allow_no_value=True)
    sealersNum = 0
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'r') as config_file:
        group_cfg.readfp(config_file)
    for node_idx, _in in enumerate(p2p_ip):
        try:
            if gm_opr:
                node_id = config.get_nodeid_str(
                    '{}/meta/gmcert_{}_{}.crt'.format(path.get_path(),
                                                      p2p_ip[node_idx], p2p_listen_port[node_idx]))
                node_id.strip('\n').strip(
                    'WARNING: can\'t open config file: /home/asherli/TASSL/ssl/openssl.cnf')
                LOGGER.info('resolve %s/meta/gmcert_%s_%s.crt',
                            path.get_path(), p2p_ip[node_idx], p2p_listen_port[node_idx])
                LOGGER.info("nodeid -> %s", node_id)
                group_cfg.set(
                    "consensus", "node.{}" .format(node_idx), node_id)
            else:
                node_id = config.get_nodeid_str(
                    '{}/meta/cert_{}_{}.crt'.format(path.get_path(),
                                                    p2p_ip[node_idx], p2p_listen_port[node_idx]))
                LOGGER.info('resolve %s/meta/cert_%s_%s.crt',
                            path.get_path(),
                            p2p_ip[node_idx],
                            p2p_listen_port[node_idx])
                LOGGER.info("nodeid -> %s", node_id)
                group_cfg.set("consensus", "node.{}".format(node_idx), node_id)
            sealersNum += 1
        except Exception as group_exp:
            LOGGER.error(
                'create group genesis failed! exception is %s', group_exp)
            raise MCError(
                'create group genesis failed! exception is %s' % group_exp)
        group_cfg.set("group", "id", group_id)
        group_cfg.set("group", "timestamp", str(time_stamp))
        group_cfg.set("consensus", "epoch_sealer_num", str(sealersNum))
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'w') as config_file:
        group_cfg.write(config_file)
    shutil.copy('{}/group.{}.genesis'.format(package_dir, group_id),
                '{}/meta/group.{}.genesis'.format(path.get_path(), group_id))

    LOGGER.info('create_group_genesis end')


def create_group_genesis_with_nodeid(data_dir='{}/meta'.format(path.get_path())):
    '''
    create group in meta
    '''
    LOGGER.info('create_group_genesis_with_nodeid start')
    package_dir = data_dir
    gm_opr = utils.Status.gm_option
    group_id = mgroup.MgroupConf.group_id
    p2p_ip = mgroup.MgroupConf.p2p_ip
    p2p_listen_port = mgroup.MgroupConf.p2p_listen_port
    utils.file_must_not_exists(
        '{}/group.{}.genesis'.format(data_dir, group_id))
    if not os.path.exists(package_dir):
        LOGGER.warning(' %s not existed!', package_dir)
        os.mkdir(data_dir)
    shutil.copy('{}/tpl/group.i.genesis'.format(path.get_path()),
                '{}/group.{}.genesis'.format(package_dir, group_id))
    shutil.copy('{}/tpl/group.i.ini'.format(path.get_path()),
                '{}/group.{}.ini'.format(package_dir, group_id))
    # updates second to ms
    (status, time_stamp) = utils.getstatusoutput('echo $(date +%s"000")')
    if not bool(status):
        CONSOLER.info('generate %s/group.%s.genesis, successful',
                      package_dir, group_id)
    else:
        LOGGER.error(
            ' Generate %s/group.%s.genesis failed! Please check your network.',
            package_dir, group_id)
        raise MCError(
            ' Generate %s/group.%s.genesis failed, timestamp is %s! Please check your network.'
            % (package_dir, group_id, time_stamp))
    # CONSOLER.info('generate %s/group.%s.ini', package_dir, group_id)
    group_cfg = configparser.ConfigParser(allow_no_value=True)
    sealersNum = 0
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'r') as config_file:
        group_cfg.readfp(config_file)
    for node_idx, _in in enumerate(p2p_ip):
        try:
            if gm_opr:
                node_id = config.get_nodeid_str_from_nodeid(
                    '{}/meta/gmnode_{}_{}.nodeid'.format(path.get_path(),
                                                         p2p_ip[node_idx], p2p_listen_port[node_idx]))
                node_id.strip('\n').strip(
                    'WARNING: can\'t open config file: /home/asherli/TASSL/ssl/openssl.cnf')
                LOGGER.info('resolve %s/meta/gmnode_%s_%s.nodeid',
                            path.get_path(), p2p_ip[node_idx], p2p_listen_port[node_idx])
                LOGGER.info("nodeid -> %s", node_id)
                group_cfg.set(
                    "consensus", "node.{}" .format(node_idx), node_id)
            else:
                node_id = config.get_nodeid_str_from_nodeid(
                    '{}/meta/node_{}_{}.nodeid'.format(path.get_path(),
                                                       p2p_ip[node_idx], p2p_listen_port[node_idx]))
                LOGGER.info('resolve %s/meta/node_%s_%s.nodeid',
                            path.get_path(),
                            p2p_ip[node_idx],
                            p2p_listen_port[node_idx])
                LOGGER.info("nodeid -> %s", node_id)
                group_cfg.set("consensus", "node.{}".format(node_idx), node_id)
            sealersNum += 1
        except Exception as group_exp:
            LOGGER.error(
                'create group genesis failed! exception is %s', group_exp)
            raise MCError(
                'create group genesis failed! exception is %s' % group_exp)
        group_cfg.set("group", "id", group_id)
        group_cfg.set("group", "timestamp", str(time_stamp))
        group_cfg.set("consensus", "epoch_sealer_num", str(sealersNum))
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'w') as config_file:
        group_cfg.write(config_file)
    shutil.copy('{}/group.{}.genesis'.format(package_dir, group_id),
                '{}/meta/group.{}.genesis'.format(path.get_path(), group_id))

    LOGGER.info('create_group_genesis_with_nodeid end')
