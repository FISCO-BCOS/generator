# coding:utf-8
"""[path.py]

Returns:
    [type] -- [description]
"""


class Path(object):
    '''
    fisco generator path configuration
    '''
    dir = ''

    def get_name(self):
        """[get some name]

        maybe it will usedful not now

        Returns:
            [string] -- [name]
        """

    def get_pylint(self):
        """[get some name]

        maybe it will usedful not now

        Returns:
            [string] -- [name]
        """


def set_path(_dir):
    """[set path]

    Arguments:
        dir {[PATH]} -- [path]
    """

    Path.dir = _dir


def get_path():
    """[get path]

    Returns:
        [PATH] -- [path]
    """

    return Path.dir
