# coding:utf-8
from pys.error.exp import MCError
from pys.log import LOGGER, CONSOLER
import sys
"""[utils.py]

Returns:
    [string] -- [utils str]
"""

import re
import os
import subprocess
import shutil
if sys.version > '3':
    import urllib.request
else:
    import urllib


class Status(object):
    """[gm Status]

    Arguments:
        object {[type]} -- [description]
    """

    gm_option = False
    unit_time = False
    allow_unsecure_cfg = False

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

    def set_allow_unsecure_cfg(self):
        """[summary]
        """

        self.allow_unsecure_cfg = True


def set_gm():
    """[set gm]
    """

    Status.gm_option = True


def off_gm():
    """[off gm]
    """

    Status.gm_option = False


def get_status():
    """[get gm or not]

    Returns:
        [bool] -- [true of false]
    """

    return Status.gm_option


def valid_chain_id(chain_id):
    """[Determine if the chain id is valid]

    Arguments:
        ip {[string]} -- [chain id]

    Returns:
        [bool] -- [true or false]
    """

    try:
        int(chain_id)
        return True
    except ValueError as utils_exp:
        LOGGER.error('%s is not a valid chain_id', utils_exp)
    except Exception as utils_exp:
        LOGGER.error('%s is not a valid chain_id', utils_exp)
        raise MCError(
            '%s is not a valid chain_id' % utils_exp)


def valid_peer(peer):
    """[Determine if the peer is valid]

    Arguments:
        peer {[str]} -- [peers]
     Returns:
        [bool] -- [true or false]
    """
    try:
        peer = peer.split(':')
        if not valid_ip(peer[0]):
            return False
        if valid_port(peer[1]):
            return True
        return False
    except ValueError as utils_exp:
        LOGGER.error('%s is not a valid peer', utils_exp)
    except Exception as utils_exp:
        LOGGER.error('%s is not a valid peer', utils_exp)
        raise MCError(
            '%s is not a valid peer' % utils_exp)


def valid_ip(_ip):
    """[Determine if the host ip is valid]

    Arguments:
        ip {[string]} -- [host ip]

    Returns:
        [bool] -- [true or false]
    """

    get_ip = re.compile(
        '^(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|[1-9])\\.(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\.'
        '(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\.(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)$')
    return bool(get_ip.match(_ip))


def valid_port(_port):
    """[Determine if the port is valid]

    Arguments:
        ip {[string]} -- [port number]

    Returns:
        [bool] -- [true or false]
    """
    port = int(_port)
    if isinstance(port, int) and (port > 1023) and (port <= 65535):
        return True
    return False


def valid_package(pkg):
    """[Determine if the string->package is valid]

    Arguments:
        pkg {[string]} -- [a string outside the function]

    Returns:
        [bool] -- [true or false]
    """
    try:
        pack = pkg.split(':')
        if not valid_ip(pack[0]):
            return False
        if int(pack[1]):
            return True
        return False
    except ValueError as utils_exp:
        LOGGER.error(' invalied package , exception is %s', utils_exp)
    except Exception as utils_exp:
        LOGGER.error(' invalied package , exception is %s', utils_exp)
        raise MCError(
            'invalied package , exception is %s' % utils_exp)


def valid_expand_package(pkg):
    """[Determine if the string->package is valid]

    Arguments:
        pkg {[string]} -- [a string outside the function]

    Returns:
        [bool] -- [true or false]
    """
    try:
        pack = pkg.split()
        if not valid_ip(pack[0]):
            return False
        if pack[1]:
            return True
        return False
    except ValueError as utils_exp:
        LOGGER.error(' invalied package , exception is %s', utils_exp)
    except Exception as utils_exp:
        LOGGER.error(' invalied package , exception is %s', utils_exp)
        raise MCError(
            'invalied package , exception is %s' % utils_exp)


def valid_string(_s):
    """[Determine if the string->s is valid]

    Arguments:
        ip {[string]} -- [a string outside the function]

    Returns:
        [bool] -- [true or false]
    """
    if sys.version > '3':
        if (isinstance(_s, (str, bytes))) and (_s):
            return True
    else:
        if (isinstance(_s, (str, unicode))) and (_s):
            return True
    return False


def replace(filepath, old, new):
    """[replace old string to new from filepath]

    Arguments:
        filepath {[path]} -- [file path that needs to be replaced]
        old {[string]} -- [old string]
        new {[string]} -- [new string]
    """
    if not os.path.exists(filepath):
        return False

    cmd = "sed -i 's|%s|%s|g' %s " % (old, new, filepath)

    status, output = getstatusoutput(cmd)
    if status != 0:
        LOGGER.error(' replace failed,'
                     'new is %s, old is %s, file is %s, status is %s, output is %s ',
                     new, old, filepath, str(status), output)
        return False
    return True


def getstatusoutput(cmd):
    """replace commands.getstatusoutput

    Arguments:
        cmd {[string]}
    """

    get_cmd = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = get_cmd.communicate()
    out = ret[0]
    err = ret[1]
    output = ''
    if not out is None:
        output = output + out.decode('utf-8')
    if not err is None:
        output = output + err.decode('utf-8')

    LOGGER.debug(' cmd is %s, status is %s, output is %s',
                 cmd, str(get_cmd.returncode), output)

    return (get_cmd.returncode, output)


def port_in_use(port):
    """using cmd nc to check if the port is occupied.

    Arguments:
        port {string} -- port number

    Returns:
        bool -- True or False.
    """

    cmd = 'nc -z 127.0.0.1' + (' %d' % port)
    status, output = getstatusoutput(cmd)

    LOGGER.debug('port is %s, status is %s, output is %s',
                 port, status, output)

    return status == 0


def delete_data(path):
    """[delete data_dir]

    Arguments:
        path {[get_dir]} -- [description]
    """

    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    else:
        LOGGER.error(' path not exisited ! path => %s', path)


def file_must_exists(_file):
    """[utils]

    Arguments:
        _file {[type]} -- [description]

    Raises:
        MCError -- [description]
    """

    if not (os.path.exists(_file) and os.path.isfile(_file)):
        LOGGER.error(' %s not exist!', _file)
        raise MCError(' %s not exist!' % _file)


def file_must_not_exists(_file):
    """[utils]

    Arguments:
        _file {[type]} -- [description]

    Raises:
        MCError -- [description]
    """

    if os.path.exists(_file) and os.path.isfile(_file):
        LOGGER.error(' %s exist! pls delete it!', _file)
        raise MCError(' %s exist! pls delete it!' % _file)


def dir_must_exists(_dir):
    """[utils]

    Arguments:
        _dir {[type]} -- [description]

    Raises:
        MCError -- [description]
    """

    if not os.path.exists(_dir):
        LOGGER.error(' %s not existed!', _dir)
        raise MCError(' %s not existed!' % _dir)


def dir_must_not_exists(_dir):
    """[utils]

    Arguments:
        _dir {[type]} -- [description]

    Raises:
        MCError -- [description]
    """

    if os.path.exists(_dir):
        LOGGER.error(' %s existed! pls delete it!', _dir)
        raise MCError(' %s existed! pls delete it!' % _dir)


def valid_node_dir(_str):
    """[summary]

    Arguments:
        _str {[type]} -- [description]
    """
    node_dir_name = _str
    pack = node_dir_name.split('_')
    if len(pack) == 3:
        if pack[0] == 'node' and valid_ip(pack[1]) and valid_port(pack[2]):
            return True
    return False


def valid_genesis(_file):
    """[summary]

    Arguments:
        _file {[type]} -- [description]
    """
    group_genesis = _file
    LOGGER.info("group genesis file is %s", group_genesis)
    pack = group_genesis.split('.')
    if len(pack) == 3:
        if pack[0] == 'group' and int(pack[1]) and pack[2] == 'genesis':
            LOGGER.info("valid_genesis is %s", pack)
            return int(pack[1])
    return 0


def get_all_nodes_dir(_dir):
    """[summary]

    Arguments:
        _dir {[type]} -- [description]
    """
    data_path = _dir
    node_dir_list = []
    dir_must_exists(data_path)
    LOGGER.info("get all nodes_dir from %s", data_path)
    for node_file in os.listdir(data_path):
        file_path = os.path.join(data_path, node_file)
        if os.path.isdir(file_path) and valid_node_dir(node_file):
            node_dir_list.append(file_path)
    LOGGER.info("all nodes_dir is %s", node_dir_list)
    return node_dir_list


def download_fisco(_dir):
    """[download fisco-bcos]

    Arguments:
        _dir {[type]} -- [description]
    """
    bin_path = _dir
    # bcos_bin_name = 'fisco-bcos'
    if Status.gm_option:
        package_name = "fisco-bcos-gm.tar.gz"
    else:
        package_name = "fisco-bcos.tar.gz"
    (status, version)\
        = getstatusoutput('curl -s https://raw.githubusercontent.com/'
                          'FISCO-BCOS/FISCO-BCOS/master/release_note.txt | sed "s/^[vV]//"')
    if bool(status):
        LOGGER.error(
            ' get fisco-bcos verion failed, result is %s.', version)
        raise MCError(' get fisco-bcos verion failed, result is %s.' % version)
    download_link = 'https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v{}/{}'.format(
        version.strip('\n'), package_name.strip('\n'))
    # filename = package_name
    LOGGER.info("Downloading fisco-bcos binary from %s", download_link)
    CONSOLER.info("Downloading fisco-bcos binary from %s", download_link)
    # (status, result) = getstatusoutput('curl -LO {}'.format(download_link))
    # subprocess.call('curl -LO {}'.format(download_link), shell=True)
    download_bin(download_link, package_name)
    # if bool(status):
    #     LOGGER.error(
    #         ' download fisco-bcos failed, result is %s.', result)
    #     raise MCError(
    #         ' download fisco-bcos failed, result is %s.' % result)
    (status, result)\
        = getstatusoutput('tar -zxf {} && mv fisco-bcos {} && rm {}'.format(package_name,
                                                                            bin_path,
                                                                            package_name))
    if bool(status):
        LOGGER.error(
            ' Decompress fisco-bcos failed, result is %s.', result)
        raise MCError(
            ' Decompress fisco-bcos failed, result is %s.' % result)
    (status, result) = getstatusoutput('chmod a+x {}'.format(bin_path))
    if bool(status):
        LOGGER.error(
            ' exec fisco-bcos failed, result is %s.', result)
        raise MCError(
            ' exec fisco-bcos failed, result is %s.' % result)
    LOGGER.info("Downloading fisco-bcos successful, fisco-bcos at %s", bin_path)
    CONSOLER.info(
        "Downloading fisco-bcos successful, fisco-bcos at %s", bin_path)


def download_console(_dir):
    """[summary]

    Arguments:
        _dir {[type]} -- [description]

    Raises:
        MCError -- [description]
        MCError -- [description]
    """

    bin_path = _dir
    package_name = "console.tar.gz"
    dir_must_not_exists('{}/console'.format(bin_path))
    (status, version) = getstatusoutput('curl -s https://raw.githubusercontent.com/'
                                        'FISCO-BCOS/console/master/release_note.txt'
                                        ' | sed "s/^[vV]//"')
    if bool(status):
        LOGGER.error(
            ' get fisco-bcos verion failed, result is %s.', version)
        raise MCError(' get fisco-bcos verion failed, result is %s.' % version)
    download_link = 'https://github.com/FISCO-BCOS/console/releases/download/v{}/{}'.format(
        version.strip('\n'), package_name.strip('\n'))
    LOGGER.info("Downloading console binary %s", download_link)
    CONSOLER.info("Downloading console binary %s", download_link)
    download_bin(download_link, package_name)
    # subprocess.call('curl -LO {}'.format(download_link), shell=True)
    (status, result)\
        = getstatusoutput('tar -zxf {} -C {} && '
                          'rm {}'.format(package_name,
                                         bin_path,
                                         package_name))
    if bool(status):
        LOGGER.error(
            ' Decompress console failed, result is %s.', result)
        raise MCError(
            ' Decompress console failed, result is %s.' % result)
    (status, result) = getstatusoutput(
        'chmod a+x {}/console/start.sh'.format(bin_path))


def _hook_func(num, block_size, total_size):
    """[get download msg]

    Arguments:
        num {[type]} -- [description]
        block_size {[type]} -- [description]
        total_size {[type]} -- [description]
    """

    precent = min(100, 100.0*num*block_size/total_size)
    sys.stdout.write('Downloading progress %.2f%%\r' % (precent))
    sys.stdout.flush()


def download_bin(_download_link, _package_name):
    """dowloand
    """
    if sys.version > '3':
        urllib.request.urlretrieve(_download_link, _package_name, _hook_func)
    else:
        urllib.urlretrieve(_download_link, _package_name, _hook_func)


def check_fisco(_file):
    """checkfisco
    """
    bin_fisco = _file
    CONSOLER.info(" Checking fisco-bcos binary...")
    LOGGER.info(" Checking fisco-bcos binary...")
    (status, bin_version)\
        = getstatusoutput('{} -v'.format(bin_fisco))
    if bool(status):
        LOGGER.error(
            'Checking fisco-bcos failed! status is %d,'
            ' output is %s, dir is %s.', status, bin_version, bin_fisco)
        raise MCError('Checking fisco-bcos failed!'
                      ' status is %d, output is %s, dir is %s.' % (
                          status, bin_version, bin_fisco))
    if not 'FISCO-BCOS' in bin_version:
        LOGGER.error(
            "%s is wrong. Please correct it and try again.", bin_fisco)
        raise Exception(
            "%s is wrong. Please correct it and try again." % bin_fisco)
    if Status.gm_option:
        if not 'gm' in bin_version:
            LOGGER.error(
                'Checking fisco-bcos failed! %s isn\'t '
                'gm version. Please correct it and try again.', bin_fisco)
            raise MCError(
                'Checking fisco-bcos failed! %s isn\'t '
                'gm version. Please correct it and try again' % bin_version)
    else:
        if 'gm' in bin_version:
            LOGGER.error(
                'Checking fisco-bcos failed! %s isn\'t '
                'standard version. Please correct it and try again.', bin_fisco)
            raise MCError(
                'Checking fisco-bcos failed! %s isn\'t '
                'standard version. Please correct it and try again.' % bin_version)
    CONSOLER.info(' Binary check passed.')
    LOGGER.info(' Binary check passed.')
