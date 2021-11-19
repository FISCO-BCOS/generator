#!/usr/bin/python
# -*- coding: UTF-8 -*-
from controller.node_controller import NodeController
from common import utilities


class NodeCommandImpl:
    def __init__(self, config):
        self.node_controller = NodeController(config)

    def gen_node_config(self):
        utilities.print_split_info()
        utilities.print_badage("generate config for all nodes")
        ret = self.node_controller.generate_all_config()
        if ret is True:
            utilities.print_badage("generate config for all nodes success")
        else:
            utilities.log_error("generate config for all nodes failed")
        utilities.print_split_info()
        return ret

    def start_all(self):
        utilities.print_split_info()
        utilities.print_badage("start all nodes of the given group")
        ret = self.node_controller.start_group()
        if ret is True:
            utilities.print_badage(
                "start all nodes of the given group success")
        else:
            utilities.log_error("start all nodes of the given group failed")
        utilities.print_split_info()
        return ret

    def stop_all(self):
        utilities.print_split_info()
        utilities.print_badage("stop all nodes of the given group")
        ret = self.node_controller.stop_group()
        if ret is True:
            utilities.print_badage("stop all nodes of the given group success")
        else:
            utilities.log_error("stop all nodes of the given group failed")
        utilities.print_split_info()
        return ret

    def upgrade_nodes(self):
        utilities.print_split_info()
        utilities.print_badage("upgrade all nodes of the given group")
        ret = self.node_controller.upgrade_group()
        if ret is True:
            utilities.print_badage(
                "upgrade all nodes of the given group success")
        else:
            utilities.log_error("upgrade all nodes of the given group failed")
        utilities.print_split_info()
        return ret

    def deploy_nodes(self):
        utilities.print_split_info()
        utilities.print_badage("deploy all nodes of the given group")
        ret = self.node_controller.generate_and_deploy_group_services()
        if ret is True:
            utilities.print_badage(
                "deploy all nodes of the given group success")
        else:
            utilities.log_error("deploy all nodes of the given group failed")
        utilities.print_split_info()
        return ret

    def upload_nodes(self):
        utilities.print_split_info()
        utilities.print_badage("upload all nodes config of the given group")
        ret = self.node_controller.deploy_group_services()
        if ret is True:
            utilities.print_badage(
                "upload all nodes config of the given group success")
        else:
            utilities.log_error(
                "upload all nodes config of the given group failed")
        utilities.print_split_info()
        return ret

    def undeploy_nodes(self):
        utilities.print_split_info()
        utilities.print_badage("undeploy all nodes of the given group")
        ret = self.node_controller.undeploy_group()
        if ret is True:
            utilities.print_badage(
                "undeploy all nodes of the given group success")
        else:
            utilities.log_error("undeploy all nodes of the given group failed")
        utilities.print_split_info()
        return ret
