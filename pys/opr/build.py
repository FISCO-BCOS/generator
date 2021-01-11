"""[--build]
"""
import os
import shutil
from pys.build import config
from pys.tool import utils
from pys import path
from pys.conf import mconf
from pys.opr import opr_cert
from pys.log import CONSOLER


def build(peer_path, data_path):
    """[--build]
    """
    utils.file_must_exists('{}/meta/fisco-bcos'.format(path.get_path()))
    utils.check_fisco('{}/meta/fisco-bcos'.format(path.get_path()))
    if utils.Status.gm_option:
        utils.file_must_exists('{}/meta/gmca.crt'.format(path.get_path()))
    else:
        utils.file_must_exists('{}/meta/ca.crt'.format(path.get_path()))
    utils.file_must_exists(peer_path)
    mconf.read_peers(peer_path)
    config.build_config_ini(data_path)
    opr_cert.deploy_key('{}/meta'.format(path.get_path()), data_path)


def package(data_path, peer_path):
    utils.file_must_exists('{}/meta/fisco-bcos'.format(path.get_path()))
    utils.check_fisco('{}/meta/fisco-bcos'.format(path.get_path()))
    if (os.path.exists(peer_path) and os.path.isfile(peer_path)):
        mconf.read_peers(peer_path)
    else:
        mconf.default_peers()
    config.build_package_only(data_path)


def build_console(_console_dir):
    """[download console]

    Arguments:
        _console_dir {[type]} -- [description]
    """
    data = _console_dir
    utils.download_console(data)
    CONSOLER.info(
        "download console success, obtain the sdk certificates now...")
    if utils.Status.gm_ssl:
        opr_cert.get_console_cert_gmssl('{}/console/conf'.format(data))
    else:
        opr_cert.get_console_cert('{}/console/conf'.format(data))
    CONSOLER.info(
        "obtain the sdk certificates success, configure the console now")
    if utils.console_use_xml_configuration():
        CONSOLER.info("configure applicationContext.xml")
        shutil.copyfile('{}/tpl/applicationContext.xml'.format(path.get_path()),
                        '{}/console/conf/applicationContext.xml'.format(data))
        config.get_console_file(
            '{}/console/conf/applicationContext.xml'.format(data))
    else:
        CONSOLER.info("configure config-example.toml")
        # copy the config-example.toml to config.toml
        shutil.copyfile('{}/console/conf/config-example.toml'.format(data),
                        '{}/console/conf/config.toml'.format(data))
        # update the connections
        config.config_console_toml_file(
            '{}/console/conf/config.toml'.format(data))
    CONSOLER.info("configure the console success")


def get_sdk(_dir):
    """[summary]

    Arguments:
        _dir {[type]} -- [description]
    """
    data = _dir
    utils.dir_must_not_exists(_dir)
    os.mkdir(_dir)
    if utils.Status.gm_ssl:
        opr_cert.get_console_cert_gmssl(_dir)
    else:
        opr_cert.get_console_cert(_dir)
    shutil.copyfile('{}/tpl/applicationContext.xml'.format(path.get_path()),
                    '{}/applicationContext.xml'.format(data))
    config.get_console_file(
        '{}/applicationContext.xml'.format(data))


def download_tassl():
    """[download_tassl]
    """
    os.chdir('{}/scripts/gm/'.format(path.get_path()))
    (status, result) = utils.getstatusoutput('./cts.sh download_tassl')
    os.chdir('{}'.format(path.get_path()))
    if bool(status):
        raise EOFError(' download tassl failed failed! status is %d, output is %s.' % (
            status, result))
