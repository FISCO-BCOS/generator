# coding:utf-8
"""[pys.tool java.py]

Raises:
    MCError -- [java version failed]

Returns:
    [string] -- [java version]
"""

from pys.error.exp import MCError
from pys.log import LOGGER
from pys.tool import utils


class JAVA(object):
    """[java verison]

    Raises:
        MCError -- [java version get]

    Returns:
        [string] -- [java version]
    """

    def __init__(self):
        """[init]
        """

        self.major = ''
        self.minor = ''
        self.openjdk = False
        self.check_java()

    def is_suitable(self):
        """[java version check]

        Returns:
            [bool] -- [true or false]
        """

        version = int('%s%s' % (self.major, self.minor))
        return (version > 18) or ((version == 18) and (not self.is_openjdk()))

    def __repr__(self):
        """[__repr__]

        Returns:
            [string] -- [java version]
        """

        if self.is_openjdk():
            return ' java version : %s.%s-%s' % (self.major, self.minor, 'openjdk')
        return ' java version : %s.%s-%s' % (self.major, self.minor, 'oracle')

    def is_openjdk(self):
        """[version chedk]

        Returns:
            [bool] -- [true or false]
        """

        return self.openjdk

    def check_java(self):
        """[check java]

        Raises:
            MCError -- [java not install]
        """

        cmd = 'java -version'
        status, output = utils.getstatusoutput(cmd)
        if status != 0:
            LOGGER.error(
                ' java -version failed , status is %d, output is %s', status, output)
            raise MCError(' java -version failed , java not installed.')

        version_str = output.split("\"")
        if not len(version_str) > 1:
            LOGGER.error(
                ' cannot get java version, status is %d, output is %s', status, output)
            raise MCError(
                ' cannot get java version, oracle jdk need >=1.8, please try \'java -version\'. ')

        version_arr = version_str[1].split('.')
        if not len(version_arr) > 2:
            LOGGER.error(
                ' cannot get java version, status is %d, output is %s', status, output)
            raise MCError(
                ' cannot get java version, oracle jdk need >=1.8, please try \'java -version\' ')

        self.major = version_arr[0]
        self.minor = version_arr[1]
        self.openjdk = bool(output.lower().find('openjdk') != -1)

        if not self.is_suitable():
            raise MCError(
                ' invalid java version, oracle jdk need >=1.8, now %s ' % self)

        LOGGER.info(' java version is %s ', self)
