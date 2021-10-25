#!/usr/bin/python
# -*- coding: UTF-8 -*-

from config.service_config_generator import ServiceConfigGenerator
from service.tars_service import TarsService
from common.utilities import ServiceInfo
from common import utilities
import os


class ServiceController:
    """
    common controller for rpc/gateway
    """

    def __init__(self, config, service_type):
        self.config = config
        self.service_type = service_type
        self.service_dict = self.config.rpc_config
        if self.service_type == ServiceInfo.gateway_service_type:
            self.service_dict = self.config.gateway_config

    def deploy_all(self):
        for service in self.service_dict.values():
            ret = self.deploy_service(service)
            if ret is False:
                utilities.log_error("deploy service %s failed" % service.name)

    def stop_all(self):
        for service in self.service_dict.values():
            ret = self.stop_service(service)
            if ret is False:
                utilities.log_error("stop service %s failed" % service.name)

    def start_all(self):
        for service in self.service_dict.values():
            ret = self.start_service(service)
            if ret is False:
                utilities.log_error("start service %s failed" % service.name)

    def undeploy_all(self):
        for service in self.service_dict.values():
            ret = self.undeploy_service(service)
            if ret is False:
                utilities.log_error(
                    "undeploy service %s failed" % service.name)

    def upgrade_all(self):
        for service in self.service_dict.values():
            ret = self.upgrade_service(service)
            if ret is False:
                utilities.log_error("upgrade service %s failed" % service.name)

    def gen_all_service_config(self):
        for service in self.service_dict.values():
            ret = self.gen_service_config(service)
            if ret is False:
                utilities.log_error(
                    "gen configuaration for service %s failed" % service.name)

    def gen_service_config(self, service_config):
        config_generator = ServiceConfigGenerator(
            self.config, self.service_type, service_config)
        return config_generator.generate_all_config()

    def deploy_service(self, service_config):
        config_generator = ServiceConfigGenerator(
            self.config, self.service_type, service_config)
        tars_service = TarsService(self.config.tars_config.tars_url,
                                   self.config.tars_config.tars_token, self.config.chain_id, service_config.deploy_ip)
        # create application
        tars_service.create_application()
        # create the service
        org_service_name = self.get_org_service_name()
        obj_name = org_service_name + "Obj"
        obj_list = [obj_name]
        # deploy service
        ret = tars_service.deploy_single_service(service_config.name, obj_list)
        if ret is False:
            return False
        return self.upgrade_service_by_config_info(tars_service, service_config, org_service_name, config_generator)

    def get_org_service_name(self):
        org_service_name = ServiceInfo.gateway_service
        if self.service_type == ServiceInfo.rpc_service_type:
            org_service_name = ServiceInfo.rpc_service
        return org_service_name

    def upgrade_service(self, service_config):
        config_generator = ServiceConfigGenerator(
            self.config, self.service_type, service_config)
        tars_service = TarsService(self.config.tars_config.tars_url,
                                   self.config.tars_config.tars_token, self.config.chain_id, service_config.deploy_ip)
        return self.upgrade_service_by_config_info(tars_service, service_config, self.get_org_service_name(), config_generator)

    def upgrade_service_by_config_info(self, tars_service, service_config, org_service_name, config_generator):
        # upload package
        (ret, patch_id) = self.upload_package(
            tars_service, service_config.name, org_service_name)
        if ret is False:
            return False
        # add configuration files
        ret = tars_service.add_config_list(
            config_generator.config_file_list, service_config.name, config_generator.config_path_list)
        if ret is False:
            return False
        # patch tars
        # get the service info
        (ret, server_id) = tars_service.get_server_id(service_config.name)
        if ret is False:
            return False
        return tars_service.patch_tars(server_id, patch_id)

    def undeploy_service(self, service_config):
        tars_service = TarsService(self.config.tars_config.tars_url,
                                   self.config.tars_config.tars_token, self.config.chain_id, service_config.deploy_ip)
        return tars_service.undeploy_tars(service_config.name)

    def start_service(self, service_config):
        tars_service = TarsService(self.config.tars_config.tars_url,
                                   self.config.tars_config.tars_token, self.config.chain_id, service_config.deploy_ip)
        return tars_service.restart_server(service_config.name)

    def stop_service(self, service_config):
        tars_service = TarsService(self.config.tars_config.tars_url,
                                   self.config.tars_config.tars_token, self.config.chain_id, service_config.deploy_ip)
        return tars_service.stop_server(service_config.name)

    def upload_package(self, tars_service, service_name, org_service_name):
        (ret, package_path) = utilities.try_to_rename_tgz_package(
            self.config.tars_config.tars_pkg_dir, service_name, org_service_name)
        if ret is False:
            utilities.log_error(
                "upload package for service %s failed for rename package name failed" % service_name)
            return (False, -1)
        return tars_service.upload_tars_package(service_name, package_path)
