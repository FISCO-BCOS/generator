"""[opr_cert]
"""
import os
import shutil
from pys import path
from pys.log import LOGGER, CONSOLER
from pys.tool import ca
from pys.error.exp import MCError
from pys.conf import mconf
from pys.tool import utils


def gen_build_cert(_dir):
    """[gen_build_cert]

    Arguments:
        _dir {[PATH]} -- [cert output]

    Raises:
        MCError -- [description]
    """

    meta_path = '{}/meta'.format(path.get_path())
    cert_path = _dir
    data_path = meta_path

    p2p_listen_port = mconf.MchainConf.p2p_listen_port
    p2p_ip = mconf.MchainConf.p2p_ip
    utils.file_must_not_exists('{}/peers.txt'.format(cert_path))
    if not os.path.exists(cert_path):
        os.mkdir(cert_path)
    if not os.path.exists('{}/ca.crt'.format(meta_path)):
        CONSOLER.error(" ca.crt not existed")
        utils.delete_data(cert_path)
        raise MCError(
            ' ca.crt not found in!')
    if not (os.path.exists('{}/agency.key'.format(meta_path))
            and os.path.exists(('{}/agency.crt'.format(meta_path)))):
        CONSOLER.error(" agency.crt or agency.key not existed")
        utils.delete_data(cert_path)
        raise MCError(
            ' agency.crt or agency.key not found in %s!' % meta_path)
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      data_path, node_ip, p2p_listen_port[my_node_index])
        if os.path.exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                     node_ip,
                                                     p2p_listen_port[my_node_index])):
            CONSOLER.error(('%s/cert_%s_%s.crt exist!!!', meta_path,
                            node_ip,
                            p2p_listen_port[my_node_index]))
            LOGGER.error(('%s/cert_%s_%s.crt exist!!!', meta_path,
                          node_ip,
                          p2p_listen_port[my_node_index]))
            raise MCError(
                '%s/cert_%s_%s.crt exist!!!' % (meta_path,
                                                node_ip,
                                                p2p_listen_port[my_node_index]))
        else:
            ca.generator_node_ca(data_path, '{}/'.format(meta_path),
                                 'node_{}_{}'.format(node_ip, p2p_listen_port[my_node_index]))
            utils.file_must_not_exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                                  node_ip,
                                                                  p2p_listen_port[my_node_index]))
            shutil.copyfile('{}/node_{}_{}/node.crt'.format(data_path,
                                                            node_ip,
                                                            p2p_listen_port[my_node_index]),
                            '{}/cert_{}_{}.crt'.format(meta_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]))
            shutil.copyfile('{}/cert_{}_{}.crt'.format(meta_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]),
                            '{}/cert_{}_{}.crt'.format(cert_path,
                                                       node_ip,
                                                       p2p_listen_port[my_node_index]))
            (status, result) = utils.getstatusoutput('echo {}:{} >> {}/peers.txt'.format(node_ip,
                                                          p2p_listen_port[my_node_index],
                                                          cert_path))
        CONSOLER.info(" status is %s, result is %s", status, result)
    CONSOLER.info(" Generate cert by node_installation.ini successful!")


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
    LOGGER.info("get cert in  %s!", get_node_list)
    LOGGER.info("send cert to %s!", send_node_list)

    for node_dir in get_node_list:
        utils.file_must_exists('{}/{}/node.key'.format(meta_path, node_dir))
        if os.path.exists('{}/{}/conf'.format(data_path, node_dir)):
            LOGGER.info("send cert from %s to %s", data_path, node_dir)
            shutil.copyfile('{}/{}/node.key'.format(meta_path, node_dir),
                            '{}/{}/conf/node.key'.format(data_path, node_dir))
        else:
            LOGGER.warning(
                ('%s not existed in %s/conf! skipped!!', node_dir, data_path))
