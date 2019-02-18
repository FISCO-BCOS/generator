# coding:utf-8
"""[version.py]

Raises:
    MCError -- [version exp]

Returns:
    [bool] -- [true or false]
"""

import os
from pys.error.exp import MCError
from pys.log import LOGGER
from pys.tool import utils


class Fisco(object):
    """[summary]

    Raises:
        MCError -- [version exp]


    Returns:
        [string] -- [fisco version]
    """

    def __init__(self, fisco_path):
        """[init]

        Arguments:
            fisco_path {[type]} -- [description]
        """

        self.fisco_path = fisco_path
        self.major = ''
        self.minor = ''
        self.revision = ''
        self.guomi = False
        self.check_fisco_version()

    def __repr__(self):
        """[repr]

        Returns:
            [type] -- [description]
        """

        if self.guomi:
            return 'fisco bcos : %s:%s:%s-%s' % (self.major, self.minor, self.revision, 'guomi')
        return 'fisco bcos : %s:%s:%s' % (self.major, self.minor, self.revision)

    def is_13_version(self):
        """[version 1.3]

        Returns:
            [type] -- [description]
        """

        return self.major == '1' and self.minor == '3'

    def is_15_version(self):
        """[version 1.5]

        Returns:
            [type] -- [description]
        """

        return self.major == '1' and self.minor == '5'

    def is_20_version(self):
        """[version 2.0]

        Returns:
            [type] -- [description]
        """

        return self.major == '2' and self.major == '0'

    def is_gm(self):
        """[version guomi]

        Returns:
            [type] -- [description]
        """

        return self.guomi

    def get_fisco_path(self):
        """[fisco path]

        Returns:
            [type] -- [description]
        """

        return self.fisco_path

    def check_fisco_version(self):
        """[check fisco version]

        Raises:
            MCError -- [description]
            MCError -- [description]
            MCError -- [description]
            MCError -- [description]
            MCError -- [description]
        """

        # check if fisco-bcos exists
        if not (os.path.exists(self.fisco_path) and os.path.isfile(self.fisco_path)):
            LOGGER.error(
                ' fisco-bcos not exist, fisco-bcos is %s', self.fisco_path)
            raise MCError(' fisco-bcos not exist, fisco-bcos is %s' %
                          self.fisco_path)

        cmd = self.fisco_path + ' --version'
        status, output = utils.getstatusoutput(cmd)
        if status != 0:
            LOGGER.error(' fisco-bcos --version failed, '
                         'fisco-bcos is %s, status is %d, output is %s',
                         self.fisco_path, status, output)
            raise MCError(
                'fisco-bcos --version failed , fisco-bcos is %s.' % self.fisco_path)

        LOGGER.debug(
            ' fisco-bcos --version, status is %d, output is %s', status, output)

        version_info = output.split()
        if version_info[0] == 'FISCO-BCOS' and len(version_info) > 2:
            version = version_info[2].split('.')
            if not len(version) == 3:
                LOGGER.error(
                    ' invalid format, 00 status is %d, output is %s', status, output)
                raise MCError('  format , fisco-bcos is %s, version is %s.' %
                              (self.fisco_path, version_info[2]))

            if version[2].endswith('-gm'):
                self.guomi = True
            self.major = str(int(version[0]))
            self.minor = str(int(version[1]))
            if self.guomi:
                self.revision = str(int(version[2][:-3]))
            else:
                self.revision = str(int(version[2]))

            LOGGER.info(' fisco-bcos is %s', self)

            # parser fisco-bcos version and check it.
            if not self.is_20_version():
                LOGGER.error(
                    ' fisco-bcos is not 2.0 version, not support now, %s', self.revision)
                raise MCError(
                    ' fisco-bcos is not 2.0 version, not support now, %s' % self.revision)

        else:
            LOGGER.error(' invalid format, fisco-bcos is %s, status is %d, output is %s',
                         self.fisco_path, status, output)
            raise MCError(' invalid format , fisco-bcos is %s, status is %d, output is %s.'
                          % (self.fisco_path, status, output))
