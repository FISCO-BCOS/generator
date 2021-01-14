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
    if utils.Status.gm_option:
        if not os.path.exists('{}/gmca.crt'.format(meta_path)):
            CONSOLER.error(" gmca.crt not existed")
            utils.delete_data(cert_path)
            raise MCError(
                ' gmca.crt not founded!')
    else:
        if not os.path.exists('{}/ca.crt'.format(meta_path)):
            CONSOLER.error(" ca.crt not existed")
            utils.delete_data(cert_path)
            raise MCError(
                ' ca.crt not founded!')
    if utils.Status.gm_option:
        if not (os.path.exists('{}/gmagency.key'.format(meta_path))
                and os.path.exists(('{}/gmagency.crt'.format(meta_path)))):
            CONSOLER.error(" gmagency.crt or gmagency.key not existed")
            utils.delete_data(cert_path)
            raise MCError(
                ' gmagency.crt or gmagency.key not found in %s!' % meta_path)
    else:
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
        if utils.Status.gm_option:
            utils.file_must_not_exists('{}/gmcert_{}_{}.crt'.format(meta_path,
                                                                    node_ip,
                                                                    p2p_listen_port[my_node_index]))
        else:
            utils.file_must_not_exists('{}/cert_{}_{}.crt'.format(meta_path,
                                                                  node_ip,
                                                                  p2p_listen_port[my_node_index]))
        ca.generator_node_ca(data_path, '{}/'.format(meta_path),
                             'node_{}_{}'.format(node_ip, p2p_listen_port[my_node_index]))
        if utils.Status.gm_option:
            if not utils.Status.gm_ssl:
                utils.off_gm()
                if os.path.isdir('./.origin_cert'):
                    shutil.rmtree('./.origin_cert')
                ca.generator_node_ca('./', meta_path, '.origin_cert')
                shutil.copytree('./.origin_cert', '{}/node_{}_{}/origin_cert'.format(
                    data_path, node_ip, p2p_listen_port[my_node_index]))
                shutil.rmtree('./.origin_cert')
                utils.set_gm()
            shutil.copyfile('{}/node_{}_{}/gmnode.crt'.format(data_path,
                                                              node_ip,
                                                              p2p_listen_port[my_node_index]),
                            '{}/gmcert_{}_{}.crt'.format(meta_path,
                                                         node_ip,
                                                         p2p_listen_port[my_node_index]))
            shutil.copyfile('{}/gmcert_{}_{}.crt'.format(meta_path,
                                                         node_ip,
                                                         p2p_listen_port[my_node_index]),
                            '{}/gmcert_{}_{}.crt'.format(cert_path,
                                                         node_ip,
                                                         p2p_listen_port[my_node_index]))
        else:
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
        (status, result) = \
            utils.getstatusoutput('echo {}:{} >> {}/peers.txt'
                                  .format(node_ip,
                                          p2p_listen_port[my_node_index],
                                          cert_path))
        LOGGER.info(" status is %s, result is %s", status, result)
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
        if not utils.valid_node_dir(node_dir):
            continue
        if utils.Status.gm_option:
            utils.file_must_exists(
                '{}/{}/gmnode.key'.format(meta_path, node_dir))
            # utils.file_must_exists(
            #     '{}/{}/gmnode.nodeid'.format(meta_path, node_dir))
            if os.path.exists('{}/{}/conf'.format(data_path, node_dir)):
                LOGGER.info("send cert from %s to %s", data_path, node_dir)
                shutil.copyfile('{}/{}/gmnode.key'.format(meta_path, node_dir),
                                '{}/{}/conf/gmnode.key'.format(data_path, node_dir))
                shutil.copyfile('{}/{}/gmnode.nodeid'.format(meta_path, node_dir),
                                '{}/{}/conf/gmnode.nodeid'.format(data_path, node_dir))
                shutil.copyfile('{}/{}/gmennode.key'.format(meta_path, node_dir),
                                '{}/{}/conf/gmennode.key'.format(data_path, node_dir))
                shutil.copyfile('{}/{}/gmennode.crt'.format(meta_path, node_dir),
                                '{}/{}/conf/gmennode.crt'.format(data_path, node_dir))
                if not utils.Status.gm_ssl:
                    shutil.copytree('{}/{}/origin_cert'.format(meta_path, node_dir),
                                    '{}/{}/conf/origin_cert'.format(data_path, node_dir))
        else:
            utils.file_must_exists(
                '{}/{}/node.key'.format(meta_path, node_dir))
            # utils.file_must_exists(
            #     '{}/{}/node.nodeid'.format(meta_path, node_dir))
            if os.path.exists('{}/{}/conf'.format(data_path, node_dir)):
                LOGGER.info("send cert from %s to %s", data_path, node_dir)
                shutil.copyfile('{}/{}/node.key'.format(meta_path, node_dir),
                                '{}/{}/conf/node.key'.format(data_path, node_dir))
                shutil.copyfile('{}/{}/node.nodeid'.format(meta_path, node_dir),
                                '{}/{}/conf/node.nodeid'.format(data_path, node_dir))

def get_console_cert(_dir):
    """get console certs

    Arguments:
        _dir {[type]} -- [description]
    """
    LOGGER.info("get console in  %s!", _dir)
    CONSOLER.info("get console in  %s!", _dir)
    meta = '{}/meta'.format(path.get_path())
    data = _dir
    get_sdk_cert()
    utils.dir_must_exists(data)
    shutil.copyfile('{}/ca.crt'.format(meta),
                    '{}/ca.crt'.format(data))
    shutil.copyfile('{}/sdk/node.key'.format(meta),
                    '{}/node.key'.format(data))
    shutil.copyfile('{}/sdk/node.crt'.format(meta),
                    '{}/node.crt'.format(data))
    shutil.copyfile('{}/sdk/node.key'.format(meta),
                    '{}/sdk.key'.format(data))
    shutil.copyfile('{}/sdk/node.crt'.format(meta),
                    '{}/sdk.crt'.format(data))

def get_console_cert_gmssl(_dir):
    """get console certs

    Arguments:
        _dir {[type]} -- [description]
    """
    LOGGER.info("get console in  %s!", _dir)
    CONSOLER.info("get console in  %s!", _dir)
    meta = '{}/meta'.format(path.get_path())
    data = _dir
    get_sdk_cert_gmssl()
    utils.dir_must_exists(data)
    os.mkdir('{}/gm'.format(data))
    shutil.copyfile('{}/gmca.crt'.format(meta),
                    '{}/gm/gmca.crt'.format(data))
    shutil.copyfile('{}/sdk/gmennode.key'.format(meta),
                    '{}/gm/gmensdk.key'.format(data))
    shutil.copyfile('{}/sdk/gmnode.crt'.format(meta),
                    '{}/gm/gmensdk.crt'.format(data))
    shutil.copyfile('{}/sdk/gmnode.key'.format(meta),
                    '{}/gm/gmsdk.key'.format(data))
    shutil.copyfile('{}/sdk/gmnode.crt'.format(meta),
                    '{}/gm/gmsdk.crt'.format(data))


def get_sdk_cert():
    """[summary]

    Arguments:
        _dir {[type]} -- [description]
    """
    LOGGER.info("get sdk cert in meta!")
    CONSOLER.info("get sdk cert in meta!")
    meta = '{}/meta'.format(path.get_path())
    utils.file_must_exists('{}/ca.crt'.format(meta))
    utils.file_must_exists('{}/agency.crt'.format(meta))
    utils.file_must_exists('{}/agency.key'.format(meta))
    if os.path.isdir('{}/sdk'.format(meta)):
        utils.file_must_exists('{}/sdk/ca.crt'.format(meta))
        utils.file_must_exists('{}/sdk/node.crt'.format(meta))
        utils.file_must_exists('{}/sdk/node.key'.format(meta))
        LOGGER.info("sdk cert existed!")
        CONSOLER.info("sdk cert existed!")
    else:
        LOGGER.info("generate console cert!")
        CONSOLER.info("generate console cert!")
        ca.generator_node_ca(meta, meta, 'sdk')

def get_sdk_cert_gmssl():
    """[summary]

    Arguments:
        _dir {[type]} -- [description]
    """
    LOGGER.info("get sdk cert in meta!")
    CONSOLER.info("get sdk cert in meta!")
    meta = '{}/meta'.format(path.get_path())
    utils.file_must_exists('{}/gmca.crt'.format(meta))
    utils.file_must_exists('{}/gmagency.crt'.format(meta))
    utils.file_must_exists('{}/gmagency.key'.format(meta))
    if os.path.isdir('{}/sdk'.format(meta)):
        utils.file_must_exists('{}/sdk/gmca.crt'.format(meta))
        utils.file_must_exists('{}/sdk/gmnode.crt'.format(meta))
        utils.file_must_exists('{}/sdk/gmnode.key'.format(meta))
        LOGGER.info("gmssl sdk cert existed!")
        CONSOLER.info("gmssl sdk cert existed!")
    else:
        LOGGER.info("generate console cert!")
        CONSOLER.info("generate console cert!")
        ca.generator_node_ca(meta, meta, 'sdk')
