"""[opr_cert]
"""
import os
import shutil
from pys import path
from pys.log import LOGGER, CONSOLER
from pys.tool import ca
from pys.error.exp import MCError
from pys.conf import mconf, mexpand
from pys.tool import utils


def gen_build_cert(_dir):
    """[gen_build_cert]

    Arguments:
        _dir {[PATH]} -- [cert output]

    Raises:
        MCError -- [description]
    """

    meta_path = '{}/meta'.format(path.get_path())
    data_path = _dir

    p2p_listen_port = mconf.MchainConf.p2p_listen_port
    p2p_ip = mconf.MchainConf.p2p_ip
    utils.dir_must_not_exists(data_path)
    os.mkdir(data_path)
    if not os.path.exists('{}/ca.crt'.format(meta_path)):
        if not os.path.exists('{}/ca.key'.format(meta_path)):
            CONSOLER.info(" Generate ca.crt and ca.key")
            ca.generate_root_ca('{}/chain_cert/'.format(meta_path))
            shutil.copyfile('{}/chain_cert/ca.crt'.format(meta_path),
                            '{}/ca.crt'.format(meta_path))
            shutil.copyfile('{}/chain_cert/ca.key'.format(meta_path),
                            '{}/ca.key'.format(meta_path))
            shutil.copyfile('{}/chain_cert/cert.cnf'.format(meta_path),
                            '{}/cert.cnf'.format(meta_path))
        else:
            LOGGER.error(
                ' ca.crt found in %s! maybe u should copy ca.key to ./meta', meta_path)
            utils.delete_data(data_path)
            raise MCError(
                ' ca.crt found in %s! maybe u should copy ca.key to ./meta' % meta_path)
    if not (os.path.exists('{}/agency.key'.format(meta_path))
            and os.path.exists(('{}/agency.crt'.format(meta_path)))):
        CONSOLER.info(" Generate agency.crt")
        ca.generator_agent_ca(meta_path, meta_path, 'agency_fisco')
        shutil.copyfile('{}/agency_fisco/agency.crt'.format(meta_path),
                        '{}/agency.crt'.format(meta_path))
        shutil.copyfile('{}/agency_fisco/agency.key'.format(meta_path),
                        '{}/agency.key'.format(meta_path))
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      data_path, node_ip, p2p_listen_port[my_node_index])
        if os.path.exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                     node_ip,
                                                     p2p_listen_port[my_node_index])):
            CONSOLER.warning(('%s/cert_%s_%s.crt exist! skipped!!', meta_path,
                              node_ip,
                              p2p_listen_port[my_node_index]))
            LOGGER.warning(('%s/cert_%s_%s.crt exist! skipped!!', meta_path,
                            node_ip,
                            p2p_listen_port[my_node_index]))
        else:
            ca.generator_node_ca(data_path, '{}/'.format(meta_path),
                                 'node_{}_{}'.format(node_ip, p2p_listen_port[my_node_index]))
            os.system('cat {}/agency.crt >>'
                      ' {}/node_{}_{}/node.crt'.format(meta_path,
                                                       data_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]))
            utils.file_must_not_exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                                  node_ip,
                                                                  p2p_listen_port[my_node_index]))
            shutil.copyfile('{}/node_{}_{}/node.crt'.format(data_path,
                                                            node_ip,
                                                            p2p_listen_port[my_node_index]),
                            '{}/cert_{}_{}.crt'.format(meta_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]))
    CONSOLER.info(" Generate cert by mchain.ini successful!")


def gen_expand_cert(_dir):
    """[gen_expand_cert]

    Arguments:
        _dir {[PATH]} -- [cert output]

    Raises:
        MCError -- [description]
    """

    meta_path = '{}/meta'.format(path.get_path())
    data_path = _dir

    p2p_listen_port = mexpand.MexpandConf.p2p_listen_port
    p2p_ip = mexpand.MexpandConf.p2p_ip
    utils.dir_must_not_exists(data_path)
    os.mkdir(data_path)
    if not (os.path.exists('{}/ca.crt'.format(meta_path))
            and os.path.exists('{}/ca.key'.format(meta_path))
            and os.path.exists('{}/cert.cnf'.format(meta_path))):
        LOGGER.error(
            ' ca.crt or ca.key or cert.cnf not existed! maybe u should copy it to ./meta')
        utils.delete_data(data_path)
        raise MCError(
            ' ca.crt or ca.key or cert.cnf not existed! maybe u should copy it to ./meta')
    if not (os.path.exists('{}/agency.key'.format(meta_path))
            and os.path.exists(('{}/agency.crt'.format(meta_path)))):
        CONSOLER.info("generate agency.crt")
        ca.generator_agent_ca(meta_path, meta_path, 'agency_expand')
        shutil.copyfile('{}/agency_expand/agency.crt'.format(meta_path),
                        '{}/agency.crt'.format(meta_path))
        shutil.copyfile('{}/agency_expand/agency.key'.format(meta_path),
                        '{}/agency.key'.format(meta_path))
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      data_path, node_ip, p2p_listen_port[my_node_index])
        if os.path.exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                     node_ip,
                                                     p2p_listen_port[my_node_index])):
            CONSOLER.warning(('%s/cert_%s_%s.crt exist! skipped!!', meta_path,
                              node_ip,
                              p2p_listen_port[my_node_index]))
            LOGGER.warning(('%s/cert_%s_%s.crt exist! skipped!!', meta_path,
                            node_ip,
                            p2p_listen_port[my_node_index]))
        else:
            ca.generator_node_ca(data_path, '{}/'.format(meta_path),
                                 'node_{}_{}'.format(node_ip, p2p_listen_port[my_node_index]))
            os.system('cat {}/agency.crt >>'
                      ' {}/node_{}_{}/node.crt'.format(meta_path,
                                                       data_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]))
            utils.file_must_not_exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                                  node_ip,
                                                                  p2p_listen_port[my_node_index]))
            shutil.copyfile('{}/node_{}_{}/node.crt'.format(data_path,
                                                            node_ip,
                                                            p2p_listen_port[my_node_index]),
                            '{}/cert_{}_{}.crt'.format(meta_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]))
    CONSOLER.info("generate cert by mexpand.ini successful!")


def deploy_key(_get_dir, _send_dir):
    """[deploy_key]

    Arguments:
        _get_dir {[PATH]} -- [description]
        _send_dir {[PATH]} -- [description]
    """

    utils.dir_must_exists(_get_dir)
    utils.dir_must_exists(_send_dir)
    meta_path = _get_dir
    data_path = _send_dir
    get_node_list = []
    send_node_list = []
    for _, dirs, _ in os.walk(meta_path, topdown=True, onerror=None, followlinks=False):
        for name in dirs:
            get_node_list.append(name)
    for _, dirs, _ in os.walk(data_path, topdown=True, onerror=None, followlinks=False):
        for name in dirs:
            send_node_list.append(name)
    CONSOLER.info(" get cert in %s!", get_node_list)
    LOGGER.info("get cert in  %s!", get_node_list)
    CONSOLER.info(" send cert to %s!", send_node_list)
    LOGGER.info("send cert to %s!", send_node_list)

    for node_dir in get_node_list:
        utils.file_must_exists('{}/{}/node.key'.format(meta_path, node_dir))
        if os.path.exists('{}/{}/conf'.format(data_path, node_dir)):
            CONSOLER.info(" send cert from %s to %s", data_path, node_dir)
            LOGGER.info("send cert from %s to %s", data_path, node_dir)
            shutil.copyfile('{}/{}/node.key'.format(meta_path, node_dir),
                            '{}/{}/conf/node.key'.format(data_path, node_dir))
        else:
            CONSOLER.warning(
                ('%s not existed in %s/conf! skipped!!', node_dir, data_path))
            LOGGER.warning(
                ('%s not existed in %s/conf! skipped!!', node_dir, data_path))
    CONSOLER.info(" doply cert successful!")
