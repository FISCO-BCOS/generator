"""[--create]
"""

from pys.build import group


def create_group(data):
    """[--create]

    Arguments:
        data {[type]} -- [description]
    """
    group.create_group_genesis(data)

def create_group_with_nodeid(data):
    """[--create]

    Arguments:
        data {[type]} -- [description]
    """
    group.create_group_genesis_with_nodeid(data)
