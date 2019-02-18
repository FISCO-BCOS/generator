# coding:utf-8
"""[version.py]
"""

from pys import path
from pys.log import CONSOLER


def version():
    """load release_node.txt, print version number.
    """

    with open('{}/release_note.txt'.format(path.get_path()), 'r') as file_releas:
        CONSOLER.info(file_releas.read())
