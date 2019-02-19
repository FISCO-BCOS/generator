"""[--demo]
"""
import os
import shutil
import configparser
from pys import path
from pys.log import LOGGER, CONSOLER
from pys.tool import ca
from pys.error.exp import MCError
from pys.conf import mconf, mexpand
from pys.opr import expand_node
from pys.opr import create_group
from pys.opr import build
from pys.log import console_print


def demo_build():
    """[demo from mchain.ini]
    """
    CONSOLER.info(
        '========== This is a build chain demo ========================='
        '===================================')
    CONSOLER.info(
        '========== After this u will build a chain in ./data depend on'
        ' ./conf/mchain.ini =================')
    CONSOLER.info(
        '========== Then u will expand this chain in ./expand depend on'
        ' ./conf/mexpand.ini ================')
    CONSOLER.info(
        '========== Then u will create a new group this chain in ./data'
        ' depend on ./conf/mgourp.ini =======')
    CONSOLER.info(
        '========== Fisco generator demo start! ==================='
        '========================================')
    LOGGER.info("build demo start ")

    p2p_listen_port = mconf.MchainConf.p2p_listen_port
    p2p_ip = mconf.MchainConf.p2p_ip
    expand_p2p_listen_port = mexpand.MexpandConf.p2p_listen_port
    expand_p2p_ip = mexpand.MexpandConf.p2p_ip

    meta_path = '{}/meta'.format(path.get_path())
    data_path = '{}/data'.format(path.get_path())
    expand_path = '{}/expand'.format(path.get_path())
    demo_path = '{}/meta/demo'.format(path.get_path())

    if os.path.exists(demo_path):
        LOGGER.error(' demo path existed! path is %s', demo_path)
        raise MCError(' demo path existed! path is %s' % demo_path)
    CONSOLER.info(
        '========== genrate demo cert and key in ./meta ==========='
        '=========================================')
    ca.generate_root_ca(demo_path)
    os.system('cp {}/ca.crt {}/ca.crt'.format(demo_path, meta_path))
    ca.generator_agent_ca(demo_path, demo_path, 'agency_fisco')
    for my_node_index, node_ip in enumerate(p2p_ip):
        LOGGER.info("p2p_ip -> %s", node_ip)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      demo_path, node_ip, p2p_listen_port[my_node_index])
        ca.generator_node_ca(demo_path, '{}/agency_fisco'.format(demo_path),
                             'node_{}_{}'.format(node_ip, p2p_listen_port[my_node_index]))
        os.system('cat {}/agency_fisco/agency.crt >>'
                  ' {}/node_{}_{}/node.crt'.format(demo_path,
                                                   demo_path,
                                                   node_ip,
                                                   p2p_listen_port[my_node_index]))
        # os.system('cat {}/ca.crt'
        #           ' >> {}/node_{}_{}/node.crt'.format(demo_path,
        #                                               demo_path,
        #                                               node_ip,
        #                                               p2p_listen_port[my_node_index]))
        os.system('cp {}/node_{}_{}/node.crt'
                  ' {}/cert_{}_{}.crt'.format(demo_path,
                                              node_ip,
                                              p2p_listen_port[my_node_index],
                                              meta_path,
                                              node_ip,
                                              p2p_listen_port[my_node_index]))
    CONSOLER.info("download lastest fisco bcos now")
    os.system('curl -LO https://raw.githubusercontent.com/'
              'FISCO-BCOS/FISCO-BCOS/release-2.0.1/tools/ci/download_bin.sh')
    os.system('bash ./download_bin.sh -o {}/'.format(meta_path))
    CONSOLER.info("download fisco bcos successful")
    CONSOLER.info(
        '========== demo --build in start ========================'
        '========================================')
    build.build(data_path)
    CONSOLER.info(
        '========== demo --build end, package in ./data ========='
        '=========================================')
    console_print("copy startall and stopall. only in demo")
    shutil.copy('{}/tpl/start_all.sh'.format(path.get_path()), data_path)
    shutil.copy('{}/tpl/stop_all.sh'.format(path.get_path()), data_path)

    console_print(
        'copy node.key to node_dir, it\'s a demo, u should do it by yourself')
    for idx, node_ip_key in enumerate(p2p_ip):
        CONSOLER.info(' copy %s/node_%s_%s/node.key',
                      demo_path, node_ip_key, p2p_listen_port[idx])
        os.system('cp {}/node_{}_{}/node.key'
                  ' {}/node_{}_{}/conf/node.key'.format(demo_path,
                                                        node_ip_key,
                                                        p2p_listen_port[idx],
                                                        data_path,
                                                        node_ip_key,
                                                        p2p_listen_port[idx]))
        ca.generator_sdk_ca('{}/node_{}_{}/'.format(data_path,
                                                     node_ip_key,
                                                     p2p_listen_port[idx]),
                             '{}/agency_fisco'.format(demo_path),
                             'sdk')
        
    CONSOLER.info(
        '========== demo --expand in start ==================='
        '=============================================')
    CONSOLER.info(
        '========== genrate expand cert and key in ./meta ==='
        '==============================================')
    for my_node_index, node_ip in enumerate(expand_p2p_ip):
        LOGGER.info("expand_p2p_ip -> %s", node_ip)
        CONSOLER.info(' Generate %s/node_%s_%s ',
                      demo_path, node_ip, expand_p2p_listen_port[my_node_index])
        ca.generator_node_ca(demo_path, '{}/agency_fisco'.format(demo_path),
                             'node_{}_{}'.format(node_ip, expand_p2p_listen_port[my_node_index]))
        os.system('cat {}/agency_fisco/agency.crt >>'
                  ' {}/node_{}_{}/node.crt'.format(demo_path,
                                                   demo_path,
                                                   node_ip,
                                                   expand_p2p_listen_port[my_node_index]))
        # os.system('cat {}/ca.crt >>'
        #           ' {}/node_{}_{}/node.crt'.format(demo_path,
        #                                            demo_path,
        #                                            node_ip,
        #                                            expand_p2p_listen_port[my_node_index]))
        os.system('cp {}/node_{}_{}/node.crt'
                  ' {}/cert_{}_{}.crt'.format(demo_path,
                                              node_ip,
                                              expand_p2p_listen_port[my_node_index],
                                              meta_path,
                                              node_ip,
                                              expand_p2p_listen_port[my_node_index]))

    CONSOLER.info(
        '========== demo --expand start ==================='
        '===============================================')
    expand_node.expand(data_path, expand_path)
    CONSOLER.info(
        '========== demo --expand end ===================='
        '================================================')
    console_print(
        'copy node.key to node_dir, it\'s a demo, u should do it by yourself')
    for idx, node_ip_key in enumerate(expand_p2p_ip):
        CONSOLER.info(' copy %s/node_%s_%s/node.key',
                      demo_path, node_ip_key, expand_p2p_listen_port[idx])
        os.system('cp {}/node_{}_{}/node.key '
                  '{}/node_{}_{}/conf/node.key'.format(demo_path,
                                                       node_ip_key,
                                                       expand_p2p_listen_port[idx],
                                                       expand_path,
                                                       node_ip_key,
                                                       expand_p2p_listen_port[idx]))
    CONSOLER.info(
        '========== demo --create start ================'
        '==================================================')
    create_group.create_group(data_path)
    CONSOLER.info(
        '========== demo --create end ================='
        '===================================================')
    CONSOLER.info(
        '========== demo finished, now u can veiw in ./meta '
        './data ./expand and start your blockchain ====')
    CONSOLER.info(
        '====you can do those steps to start your blockchain')
    CONSOLER.info(
        '========== step1: cd ./data')
    CONSOLER.info(
        '========== step2: ./start_all.sh')
    CONSOLER.info(
        '========== step3: ps -ef | grep fisco | grep -v grep')
    CONSOLER.info(
        '========== step4: tail -f node_127.0.0.1_3030*/log/log_*')
    LOGGER.info("build demo end ")
