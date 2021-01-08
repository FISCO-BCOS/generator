# coding:utf-8
"""[ca.py]

Raises:
    MCError -- [description]
    MCError -- [description]
    MCError -- [description]
"""

import os
import shutil
from pys.tool import utils
from pys import path
from pys.log import LOGGER, CONSOLER, console_error
from pys.error.exp import MCError


def generate_root_ca(_dir):
    """[generate root cert]

    Arguments:
        dir {[path]} -- [root cert path]
    """
    try:
        ca_dir = os.path.abspath(_dir)
        if utils.Status.gm_option:
            os.chdir('{}/scripts/gm/'.format(path.get_path()))
            (status, result) = utils.getstatusoutput('./cts.sh gen_chain_cert {}'
                                                     .format(ca_dir))
            os.chdir('{}'.format(path.get_path()))
        else:
            os.chdir('{}/scripts'.format(path.get_path()))
            (status, result) = utils.getstatusoutput('./cts.sh gen_chain_cert {}'
                                                     .format(ca_dir))
            os.chdir('{}'.format(path.get_path()))
        if bool(status):
            LOGGER.error(
                ' cts.sh failed! status is %d, output is %s, dir is %s.', status, result, ca_dir)
            raise MCError('cts.sh failed! status is %d, output is %s, dir is %s.' % (
                status, result, ca_dir))
        LOGGER.info(
            ' cts.sh success! status is %d, output is %s, dir is %s.', status, result, ca_dir)
        LOGGER.info(' Generate root cert success, dir is %s', ca_dir)
        CONSOLER.info(' Generate root cert success, dir is %s', ca_dir)
    except MCError as cert_exp:
        console_error('  %s ' % cert_exp)
    except Exception as gen_cert_exp:
        console_error(
            '  Generate root cert failed! excepion is %s.' % gen_cert_exp)
        LOGGER.error('  Generate root cert failed! Result is %s', result)
        raise MCError(
            'Generate root agency failed! Result is %s' % gen_cert_exp)


def generator_agent_ca(_dir, _ca, agent):
    """[generate agency cert]

    Arguments:
        dir {[path]} -- [agency cert path]
        ca {[path]} -- [root cert path]
        agent {[string]} -- [agency name]
    """
    try:
        ca_dir = os.path.abspath(_ca)
        agency_dir = os.path.abspath(_dir)
        if utils.Status.gm_option:
            os.chdir('{}/scripts/gm/'.format(path.get_path()))
            (status, result) = utils.getstatusoutput('./cts.sh'
                                                     ' gen_agency_cert {} {}/{}'
                                                     .format(ca_dir,
                                                             agency_dir, agent))
            os.chdir('{}'.format(path.get_path()))
        else:
            os.chdir('{}/scripts'.format(path.get_path()))
            (status, result) = utils.getstatusoutput('./cts.sh'
                                                     ' gen_agency_cert {} {}/{}'
                                                     .format(ca_dir,
                                                             agency_dir, agent))
            os.chdir('{}'.format(path.get_path()))
        if not bool(status):
            LOGGER.info(' Generate %s cert successful! dir is %s/%s.',
                        agent, agency_dir, agent)
        else:
            # console_error(
            #     '  Generate cert failed! Please check your network,'
            #     ' and try to check your opennssl version.')
            LOGGER.error('  Generate %s cert failed! Result is %s',
                         agent, result)
            raise MCError(' Generate %s cert failed! Result is %s' %
                          (agent, result))
    except MCError as cert_exp:
        console_error('  %s ' % cert_exp)
    except Exception as gen_cert_exp:
        console_error(
            '  Generate agency cert failed! excepion is %s.' % gen_cert_exp)
        LOGGER.error('  Generate agency cert failed! Result is %s', result)
        raise MCError(
            'Generate agency agency failed! Result is %s' % gen_cert_exp)


def generator_node_ca(_dir, agent, node):
    """[generate node cert ]

    Arguments:
        agent {[path]} -- [agency cert path]
        node {[string]} -- [node name]
        dir {[path]} -- [node cert path]
    """
    node_dir = os.path.abspath(_dir)
    agent = os.path.abspath(agent)
    try:
        if utils.Status.gm_option:
            os.chdir('{}/scripts/gm/'.format(path.get_path()))
            (status, result) = utils.getstatusoutput('./cts.sh'
                                                     ' gen_node_cert {} {}/{}'
                                                     .format(
                                                         agent, node_dir, node))
            os.chdir('{}'.format(path.get_path()))
        else:
            os.chdir('{}/scripts/'.format(path.get_path()))
            (status, result) = utils.getstatusoutput('./cts.sh'
                                                     ' gen_node_cert {} {}/{}'
                                                     .format(
                                                         agent, node_dir, node))
            os.chdir('{}'.format(path.get_path()))
        if not bool(status):
            LOGGER.info(' Generate %s cert successful! dir is %s/%s.',
                        node, node_dir, node)
            os.chdir('{}'.format(path.get_path()))
            if utils.Status.gm_option:
                (status, result) = utils.getstatusoutput('cat {}/{}/gmagency.crt '
                                                         '>> {}/{}/gmnode.crt'.format(
                                                             _dir, node, _dir, node))
                os.remove('{}/{}/gmagency.crt'.format(_dir, node))
                os.remove('{}/{}/gmnode.serial'.format(_dir, node))
            else:
                (status, result) = utils.getstatusoutput('cat {}/{}/agency.crt '
                                                         '>> {}/{}/node.crt'.format(
                                                             _dir, node, _dir, node))
                os.remove('{}/{}/agency.crt'.format(_dir, node))
                os.remove('{}/{}/node.ca'.format(_dir, node))
                os.remove('{}/{}/node.json'.format(_dir, node))
                os.remove('{}/{}/node.private'.format(_dir, node))
                os.remove('{}/{}/node.serial'.format(_dir, node))
                os.remove('{}/{}/node.param'.format(_dir, node))
                os.remove('{}/{}/node.pubkey'.format(_dir, node))
        else:
            # console_error(
            #     '  Generate node cert failed! Please check your network,'
            #     ' and try to check your opennssl version.')
            LOGGER.error('  Generate %s cert failed! Result is %s',
                         node, result)
            raise MCError(' Generate %s cert failed! Result is %s' %
                          (node, result))
    except MCError as cert_exp:
        console_error('  %s ' % cert_exp)
    except Exception as gen_cert_exp:
        console_error(
            '  Generate node cert failed! excepion is %s.' % gen_cert_exp)
        LOGGER.error('  Generate node cert failed! Result is %s', result)
        raise MCError(
            'Generate node failed! Result is %s' % gen_cert_exp)


def generator_sdk_ca(_dir, agent):
    """[generate sdk cert]

    Arguments:
        _dir {[path]} -- [node cert path]
        _agent {[path]} -- [agency cert path]
    """

    sdk_dir = os.path.abspath(_dir)
    agency_dir = os.path.abspath(agent)
    if utils.Status.gm_option:
        if not utils.Status.gm_ssl:
            utils.off_gm()
            generator_node_ca(sdk_dir, agency_dir, 'sdk')
            os.remove('{}/sdk/node.nodeid'.format(sdk_dir))
            shutil.copyfile('{}/sdk/node.crt'.format(sdk_dir),
                    '{}/sdk/sdk.crt'.format(sdk_dir))
            shutil.copyfile('{}/sdk/node.key'.format(sdk_dir),
                    '{}/sdk/sdk.key'.format(sdk_dir))
            utils.set_gm()
        generator_node_ca('{}/sdk'.format(sdk_dir), agency_dir, 'gm')
        os.remove('{}/sdk/gm/gmnode.nodeid'.format(sdk_dir))
        shutil.copyfile('{}/sdk/gm/gmnode.crt'.format(sdk_dir),
                '{}/sdk/gm/gmsdk.crt'.format(sdk_dir))
        shutil.copyfile('{}/sdk/gm/gmnode.key'.format(sdk_dir),
                '{}/sdk/gm/gmsdk.key'.format(sdk_dir))
        shutil.copyfile('{}/sdk/gm/gmennode.crt'.format(sdk_dir),
                '{}/sdk/gm/gmensdk.crt'.format(sdk_dir))
        shutil.copyfile('{}/sdk/gm/gmennode.key'.format(sdk_dir),
                '{}/sdk/gm/gmensdk.key'.format(sdk_dir))
    else:
        generator_node_ca(sdk_dir, agency_dir, 'sdk')
        os.remove('{}/sdk/node.nodeid'.format(sdk_dir))
        shutil.copyfile('{}/sdk/node.crt'.format(sdk_dir),
                '{}/sdk/sdk.crt'.format(sdk_dir))
        shutil.copyfile('{}/sdk/node.key'.format(sdk_dir),
                '{}/sdk/sdk.key'.format(sdk_dir))
