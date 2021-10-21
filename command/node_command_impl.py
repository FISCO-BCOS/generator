#!/usr/bin/python
# -*- coding: UTF-8 -*-
from controller.node_controller import NodeController


class NodeCommandImpl:
    def __init__(self, config):
        self.node_controller = NodeController(config)

    def gen_node_config(self):
        self.node_controller.generate_all_config()

    def start_all(self):
        self.node_controller.start_group()

    def stop_all(self):
        self.node_controller.stop_group()

    def upgrade_nodes(self):
        self.node_controller.upgrade_group()

    def deploy_nodes(self):
        self.node_controller.generate_and_deploy_group_services()

    def upload_nodes(self):
        self.node_controller.deploy_group_services()

    def undeploy_nodes(self):
        self.node_controller.undeploy_group()
