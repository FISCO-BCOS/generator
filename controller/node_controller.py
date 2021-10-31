#!/usr/bin/python
# -*- coding: UTF-8 -*-

from service.tars_service import TarsService
from common import utilities
from common.utilities import ServiceInfo
from config.node_config_generator import NodeConfigGenerator
import os
import time


class NodeController:
    """
    the node controller
    """

    def __init__(self, config):
        self.config = config
        self.node_config_generator = NodeConfigGenerator(config)

    def generate_all_config(self):
        nodeid_list = self.node_config_generator.generate_all_nodes_pem()
        for node_config in self.config.group_config.node_list:
            self.node_config_generator.generate_node_all_config(
                node_config, nodeid_list)

    def generate_and_deploy_group_services(self):
        utilities.log_info("generate config for chain = %s, group = %s" % (
            self.config.group_config.chain_id, self.config.group_config.group_id))
        self.generate_all_config()
        self.deploy_group_services()

    def deploy_group_services(self):
        utilities.log_info("deploy services for all the group nodes")
        for node_config in self.config.group_config.node_list:
            utilities.log_info("deploy service for node %s" %
                               node_config.node_name)
            ret = self.deploy_node_services(node_config)
            if ret is False:
                utilities.log_error(
                    "deploy service for node %s failed" % node_config.node_name)
                return False

    def get_service_list(self):
        services = []
        org_services = []
        for node in self.config.group_config.node_list:
            service_list = node.nodes_service_name_list
            for key in service_list.keys():
                service_mapping = service_list[key]
                for service_name in service_mapping.keys():
                    services.append(service_name)
                    org_services.append(service_mapping[service_name])
        return (services, org_services)

    def start_group(self):
        (service_list, _) = self.get_service_list()
        self.start_all(service_list)

    def stop_group(self):
        (service_list, _) = self.get_service_list()
        self.stop_all(service_list)

    def undeploy_group(self):
        (service_list, _) = self.get_service_list()
        self.undeploy_all(service_list)

    def start_all(self, service_list):
        tars_service_obj = TarsService(self.config.tars_config.tars_url,
                                       self.config.tars_config.tars_token, self.config.chain_id, "")
        for service in service_list:
            tars_service_obj.restart_server(service)

    def stop_all(self, service_list):
        tars_service_obj = TarsService(self.config.tars_config.tars_url,
                                       self.config.tars_config.tars_token, self.config.chain_id, "")
        for service in service_list:
            tars_service_obj.stop_server(service)

    def undeploy_all(self, service_list):
        tars_service_obj = TarsService(self.config.tars_config.tars_url,
                                       self.config.tars_config.tars_token, self.config.chain_id, "")
        for service in service_list:
            ret = tars_service_obj.undeploy_tars(service)
            if ret is False:
                utilities.log_error("undeploy service %s failed" % service)
            else:
                utilities.log_info("undeploy service %s success" % service)

    def upgrade_group(self):
        tars_service_obj = TarsService(self.config.tars_config.tars_url,
                                       self.config.tars_config.tars_token, self.config.chain_id, "")
        (service_list, org_service_list) = self.get_service_list()
        i = 0
        for service in service_list:
            org_service = org_service_list[i]
            self.upload_package(tars_service_obj, service, org_service)
            i = i + 1

    def deploy_node_services(self, node_config):
        service_list = node_config.nodes_service_name_list
        for key in service_list.keys():
            service_mapping = service_list[key]
            for service_name in service_mapping.keys():
                utilities.log_info("deploy service %s" % service_name)
                org_service_name = service_mapping[service_name]
                self.deploy_service(
                    node_config, service_name, org_service_name)
                time.sleep(5)

    def deploy_service(self, node_config, service_name, org_service_name):
        deploy_ip = node_config.service_list[org_service_name]
        tars_service_obj = TarsService(self.config.tars_config.tars_url,
                                       self.config.tars_config.tars_token, self.config.chain_id, deploy_ip)
        # create application
        tars_service_obj.create_application()
        # create service
        obj_name = org_service_name + "Obj"
        obj_list = []
        if node_config.microservice_node is True:
            obj_list.append(obj_name)
        else:
            obj_list = node_config.obj_name_list
        ret = tars_service_obj.deploy_single_service(service_name, obj_list)
        if ret is False:
            return False
        # upload_package
        (ret, patch_id) = self.upload_package(
            tars_service_obj, service_name, org_service_name)
        if ret is False:
            return False
        # add configuration
        (config_file_list, config_path_list) = self.node_config_generator.get_all_service_info(
            node_config, service_name)
        ret = tars_service_obj.add_config_list(
            config_file_list, service_name, config_path_list)
        if ret is False:
            return False
        # patch tars
        (ret, server_id) = tars_service_obj.get_server_id(service_name)
        if ret is False:
            return False
        return tars_service_obj.patch_tars(server_id, patch_id)

    def upload_package(self, tars_service, service_name, org_service_name):
        # upload the package
        (ret, package_path) = utilities.try_to_rename_tgz_package(
            self.config.tars_config.tars_pkg_dir, service_name, org_service_name)
        if ret is False:
            utilities.log_error(
                "upload package for service %s failed" % service_name)
            return (False, -1)
        return tars_service.upload_tars_package(service_name, package_path)
