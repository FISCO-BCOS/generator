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
