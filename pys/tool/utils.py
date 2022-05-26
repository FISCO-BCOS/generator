# coding:utf-8
"""[utils.py]

Returns:
    [string] -- [utils str]
"""
import sys
import re
import os
import subprocess
import shutil
from pys.error.exp import MCError
from pys.log import LOGGER, CONSOLER
from pys import path
if sys.version > '3':
    import urllib.request
    import urllib.error
else:
    import urllib
    import urllib2


class Status(object):
    """[gm Status]

    Arguments:
        object {[type]} -- [description]
    """

    gm_option = False
    gm_ssl = False
    unit_time = False
    allow_unsecure_cfg = False
    use_cdn = False
    download_console_shell_script = "download_console.sh"
    default_console_version = "2.9.0"
    download_console_version = default_console_version
    download_console_version_specified = False
    solidity_version = ""
    solidity_version_specified = False

    def __init__(self):
        """[init]
        """

        self. gm_option = False

    def get_gm_status(self):
        """[get gm_option]


        Returns:
            [string] -- [gm]
        """
        return self.gm_option

    def get_gmssl_status(self):
        """[get gm_option]


        Returns:
            [string] -- [gm]
        """
        return self.gm_ssl

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

    def get_cnd_status(self):
        """[get gm_option]


        Returns:
            [string] -- [gm]
        """
        return self.use_cdn


def set_cdn():
    """[summary]
    """

    Status.use_cdn = True


def console_use_xml_configuration():
    """
    determine to use toml or xml configuration
    (console use toml configuration since v2.6.0)
    """
    version_list = Status.download_console_version.split(".")
    if len(version_list) < 3:
        raise MCError(
            '%s invalid download_console_version' % Status.download_console_version)
    # check the major version
    major_version = version_list[0]
    if int(major_version) >= 2:
        return False
    else:
        return True


def set_download_console_version(version):
    """
    set download_console_version
    """
    Status.download_console_version = version
    Status.download_console_version_specified = True
    CONSOLER.debug("expect to download console %s",
                   Status.download_console_version)


def set_solidity_version(version):
    """
    set the solidity version, now support 0.5 and 0.6
    """
    Status.solidity_version = version
    Status.solidity_version_specified = True
    LOGGER.debug('expected solidity version is %s', Status.solidity_version)


def set_gm():
    """[set gm]
    """

    Status.gm_option = True


def set_gmssl():
    """[set gm]
    """

    Status.gm_ssl = True


def off_gm():
    """[off gm]
    """

    Status.gm_option = False


def off_gmssl():
    """[off gm]
    """

    Status.gm_ssl = False


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

    # get_ip = re.compile(
    #     '^(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|[1-9])\\.(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\.'
    #     '(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\.(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)$')
    # return bool(get_ip.match(_ip))
    return True


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
    dir_must_exists(_dir)
    bin_path = _dir

    package_name = "fisco-bcos.tar.gz"
    # (status, version)\
    #     = getstatusoutput(r'curl -s https://api.github.com/repos/FISCO-BCOS/FISCO-BCOS/releases '
    #                       r'| grep "tag_name" | grep "\"v2\.[0-9]\.[0-9]\""'
    #                       r' | sort -u | tail -n 1 | cut -d \" -f 4 | sed "s/^[vV]//"')
    # if bool(status):
    #     LOGGER.error(
    #         ' get fisco-bcos verion failed, result is %s.', version)
    #     raise MCError(' get fisco-bcos verion failed, result is %s.' % version)
    version = "2.9.0"
    download_link = 'https://github.com/FISCO-BCOS/FISCO-BCOS/releases/download/v{}/{}'.format(
        version.strip('\n'), package_name.strip('\n'))
    cnd_link = 'https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/FISCO-BCOS/FISCO-BCOS/releases/v{}/{}'.format(
        version.strip('\n'), package_name.strip('\n'))
    if Status.use_cdn:
        if valid_url(cnd_link):
            LOGGER.info("Downloading fisco-bcos binary from %s", cnd_link)
            CONSOLER.info("Downloading fisco-bcos binary from %s", cnd_link)
            download_bin(cnd_link, package_name)
        elif valid_url(download_link):
            LOGGER.info("Downloading fisco-bcos binary from %s", download_link)
            CONSOLER.info(
                "Downloading fisco-bcos binary from %s", download_link)
            download_bin(download_link, package_name)
        else:
            LOGGER.error(
                ' Download fisco-bcos failed, Please check your network!')
            raise MCError(
                ' Download fisco-bcos failed, Please check your network!')
    else:
        if valid_url(download_link):
            LOGGER.info("Downloading fisco-bcos binary from %s", download_link)
            CONSOLER.info(
                "Downloading fisco-bcos binary from %s", download_link)
            download_bin(download_link, package_name)
        else:
            LOGGER.error(
                ' Download fisco-bcos failed, Please check your network!')
            raise MCError(
                ' Download fisco-bcos failed, Please check your network!')
    (status, result)\
        = getstatusoutput('tar -zxf {} -C {} && rm {}'.format(package_name,
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

    dir_must_exists(_dir)
    bin_path = _dir
    meta = '{}/meta'.format(path.get_path())
    # file_must_exists('{}/ca.crt'.format(meta))
    # file_must_exists('{}/agency.crt'.format(meta))
    # file_must_exists('{}/agency.key'.format(meta))
    download_console_command = "bash {}/tpl/{}".format(
        path.get_path(), Status.download_console_shell_script)
    cdn_option = ""
    if Status.use_cdn:
        CONSOLER.info("download_console: use cdn")
        cdn_option = "-n"
    download_console_command = "{} {}".format(
        download_console_command, cdn_option)
    if(Status.download_console_version_specified is True):
        download_console_command = "{} -c {}".format(
            download_console_command, Status.download_console_version)

    if(Status.solidity_version_specified is True):
        download_console_command = "{} -v {}".format(
            download_console_command, Status.solidity_version)
    CONSOLER.info("The download_console_command is %s",
                  download_console_command)
    # execute the download_console_command
    (status, result) = getstatusoutput(download_console_command)
    if bool(status):
        LOGGER.error(
            ' download console failed, result is %s.', result)
        raise MCError(
            ' download console failed, result is %s.' % result)
    chmod_command = 'chmod a+x console/start.sh'
    if bin_path != "." and bin_path != "./":
        chmod_command = "{} && mv console {}".format(chmod_command, bin_path)
    (status, result) = getstatusoutput(chmod_command)
    if bool(status):
        LOGGER.error(
            'chmod console failed! status is %d,'
            ' output is %s.', status, result)
        raise MCError('chmod console failed!'
                      ' status is %d, output is %s.' % (
                          status, result))


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


def chunk_report(bytes_so_far, chunk_size, total_size):
    """[summary]

    Arguments:
        bytes_so_far {[type]} -- [description]
        chunk_size {[type]} -- [description]
        total_size {[type]} -- [description]
    """
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                     (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(response, chunk_size=8192, report_hook=None, ):
    """output download
    """
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    data = []

    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        data += chunk
        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)

    return "".join(data)


def download_bin(_download_link, _package_name):
    """dowloand
    """
    try:
        if sys.version > '3':
            urllib.request.urlretrieve(
                _download_link, _package_name, _hook_func)
        else:
            if os.environ.get('https_proxy') or os.environ.get('http_proxy'):
                url = _download_link
                response = urllib2.urlopen(url)
                data = chunk_read(response, report_hook=chunk_report)
                # data = response.read()
                with open(_package_name, 'wb') as code:
                    code.write(data)
            else:
                urllib.urlretrieve(_download_link, _package_name, _hook_func)
    except Exception as download_err:
        LOGGER.error(
            'download %s failed! exception is %s', _package_name, download_err)
        raise MCError(
            'download %s failed! exception is %s' % (_package_name, download_err))


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
    # if Status.gm_option:
    #     if not 'gm' in bin_version:
    #         LOGGER.error(
    #             'Checking fisco-bcos failed! %s isn\'t '
    #             'gm version. Please correct it and try again.', bin_fisco)
    #         raise MCError(
    #             'Checking fisco-bcos failed! %s isn\'t '
    #             'gm version. Please correct it and try again' % bin_version)
    # else:
    #     if 'gm' in bin_version:
    #         LOGGER.error(
    #             'Checking fisco-bcos failed! %s isn\'t '
    #             'standard version. Please correct it and try again.', bin_fisco)
    #         raise MCError(
    #             'Checking fisco-bcos failed! %s isn\'t '
    #             'standard version. Please correct it and try again.' % bin_version)
    CONSOLER.info(' Binary check passed.')
    LOGGER.info(' Binary check passed.')


def valid_url(_url):
    """check valid url
    """
    baseURL = _url
    # print fullURL
    try:
        if sys.version > '3':
            try:
                resp = urllib.request.urlopen(baseURL)
                return True
            except urllib.error.HTTPError as e:
                # Return code error (e.g. 404, 501, ...)
                # ...
                LOGGER.warning('HTTPError: {}'.format(e.code))
                return False
            except urllib.error.URLError as e:
                # Not an HTTP-specific error (e.g. connection refused)
                # ...
                LOGGER.warning('URLError: {}'.format(e.reason))
                return False
            LOGGER.warning('Maybe others err')
            return False
        else:
            req = urllib2.Request(baseURL)
            resp = urllib2.urlopen(req)
        if resp.getcode() == 404:
            # Do whatever you want if 404 is found
            LOGGER.warning("404 Found!")
            return False
        # Do your normal stuff here if page is found.
        LOGGER.info("URL: {0} Response: {1}".format(
            baseURL, resp.getcode()))
        return True
    except Exception as download_err:
        LOGGER.error("Could not connect to URL: %s ,err is %s",
                     baseURL, download_err)
        return False
