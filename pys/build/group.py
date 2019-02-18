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
import configparser

from pys import path
from pys.log import LOGGER, CONSOLER
from pys.error.exp import MCError
from pys.conf import mconf, mgroup
from pys.build import config


def build_group_genesis(data_dir='{}/data'.format(path.get_path())):
    """[--build generate group.genesis]

    Keyword Arguments:
        data_dir {[PATH]} -- [output path] (default: {'{}/data'.format(path.get_path())})

    Raises:
        MCError -- [description]
        MCError -- [description]
    """

    LOGGER.info('build_group_genesis start')

    # mchain = '{}/conf/mchain.ini'.format(path.get_path())
    package_dir = data_dir
    gm_opr = config.Status.gm_option
    group_id = mconf.MchainConf.group_id
    p2p_ip = mconf.MchainConf.p2p_ip
    p2p_listen_port = mconf.MchainConf.p2p_listen_port

    if not os.path.exists(package_dir):
        LOGGER.error(' ./data not existed!')
        raise MCError(' ./data not existed!')
    shutil.copy('{}/tpl/group.i.genesis'.format(path.get_path()),
                '{}/group.{}.genesis'.format(package_dir, group_id))
    shutil.copy('{}/tpl/group.i.ini'.format(path.get_path()),
                '{}/group.{}.ini'.format(package_dir, group_id))
    group_cfg = configparser.ConfigParser()
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'r') as config_file:
        group_cfg.readfp(config_file)
    for node_idx, _in in enumerate(p2p_ip):
        try:
            if gm_opr:
                node_id = config.get_nodeid_str(
                    '{}/meta/gmcert_{}_{}.crt'.format(path.get_path(),
                                                      p2p_ip[node_idx], p2p_listen_port[node_idx]))
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
        except Exception as group_exp:
            LOGGER.error(
                'create group genesis failed exception is %s', group_exp)
            raise MCError(
                'create group genesis failed exception is %s' % group_exp)
        group_cfg.set("group", "index", group_id)
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'w') as config_file:
        group_cfg.write(config_file)

    # copy group
    for my_node_index, _in in enumerate(p2p_ip):
        node_dir = '{}/node_{}_{}'.format(package_dir,
                                          p2p_ip[my_node_index], p2p_listen_port[my_node_index])
        shutil.copy('{}/group.{}.ini'.format(package_dir, group_id),
                    '{}/conf/group.{}.ini'.format(node_dir, group_id))
        shutil.copy('{}/group.{}.genesis'.format(package_dir, group_id),
                    '{}/conf/group.{}.genesis'.format(node_dir, group_id))
    LOGGER.info('build_group_genesis start')


def create_group_genesis(data_dir='{}/data'.format(path.get_path())):
    '''
    create group in meta
    '''
    LOGGER.info('create_group_genesis start')
    package_dir = data_dir
    gm_opr = config.Status.gm_option
    group_id = mgroup.MgroupConf.group_id
    p2p_ip = mgroup.MgroupConf.p2p_ip
    p2p_listen_port = mgroup.MgroupConf.p2p_listen_port

    if not os.path.exists(package_dir):
        LOGGER.warning(' ./data not existed!')
        os.mkdir(data_dir)
    shutil.copy('{}/tpl/group.i.genesis'.format(path.get_path()),
                '{}/group.{}.genesis'.format(package_dir, group_id))
    shutil.copy('{}/tpl/group.i.ini'.format(path.get_path()),
                '{}/group.{}.ini'.format(package_dir, group_id))
    CONSOLER.info('generate %s/group.%s.genesis', package_dir, group_id)
    CONSOLER.info('generate %s/group.%s.ini', package_dir, group_id)
    group_cfg = configparser.ConfigParser()
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'r') as config_file:
        group_cfg.readfp(config_file)
    for node_idx, _in in enumerate(p2p_ip):
        try:
            if gm_opr:
                node_id = config.get_nodeid_str(
                    '{}/meta/gmcert_{}_{}.crt'.format(path.get_path(),
                                                      p2p_ip[node_idx], p2p_listen_port[node_idx]))
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
        except Exception as group_exp:
            LOGGER.error(
                'create group genesis failed! exception is %s', group_exp)
            raise MCError(
                'create group genesis failed! exception is %s' % group_exp)
        group_cfg.set("group", "index", group_id)
    with open('{}/group.{}.genesis'.format(package_dir, group_id), 'w') as config_file:
        group_cfg.write(config_file)

    LOGGER.info('create_group_genesis end')
