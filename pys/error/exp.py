# coding:utf-8
"""[catch Exception]
"""

from pys.log import CONSOLER


class MCError(Exception):
    """Customize exception handling

    Arguments:
        Exception {string} -- exception description
    """

    def __init__(self, msg):
        """[init]

        Arguments:
            msg {[string]} -- [error decription]
        """

        Exception.__init__(self, msg)
        self.msg = msg

    def logout(self):
        """[output to screen]
        """

        CONSOLER.info('%s', self.msg)
