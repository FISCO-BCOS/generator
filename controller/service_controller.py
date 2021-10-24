#!/usr/bin/python
# -*- coding: UTF-8 -*-

from config.service_config_generator import ServiceConfigGenerator
from service.tars_service import TarsService
from common.utilities import ServiceInfo
import os


class ServiceController:
    """
    common controller for rpc/gateway
    """

    def __init__(self, config, service_type):
        self.config = config
        self.service_type = service_type
        self.config_generator = ServiceConfigGenerator(
            config, service_type)
        self.init(service_type)
        self.tars_service = TarsService(self.config.tars_config.tars_url, self.config.tars_config.tars_token,
                                        self.service_config.name, self.service_config.deploy_ip)

    def init(self, service_type):
        self.service_name = ServiceInfo.gateway_service
        self.service_config = self.config.gateway_config
        if service_type == ServiceInfo.rpc_service_type:
            self.service_name = ServiceInfo.rpc_service
            self.service_config = self.config.rpc_config
        self.obj_name = self.service_name + "Obj"

    def deploy_service(self):
        # create application
        self.tars_service.create_application()
        # create the service
        obj_list = [self.obj_name]
        ret = self.tars_service.deploy_single_service(
            self.service_name, obj_list)
        if ret is False:
            return False
        (ret, patch_id) = self.upload_package()
        if ret is False:
            return False
        # add configuration files
        ret = self.tars_service.add_config_list(
            self.config_generator.config_file_list, self.service_name, self.config_generator.config_path_list)
        if ret is False:
            return False
        # patch tars
        # get the service info
        (ret, server_id) = self.tars_service.get_server_id(self.service_name)
        if ret is False:
            return False
        return self.tars_service.patch_tars(server_id, patch_id)

    def undeploy_service(self):
        return self.tars_service.undeploy_tars(self.service_name)

    def start_service(self):
        return self.tars_service.restart_server(self.service_name)

    def stop_service(self):
        return self.tars_service.stop_server(self.service_name)

    def upload_package(self):
        # upload the package
        package_name = self.service_name + ServiceInfo.tars_pkg_postfix
        package_path = os.path.join(
            self.config.tars_config.tars_pkg_dir, package_name)
        return self.tars_service.upload_tars_package(self.service_name, package_path)

    def upgrade_service(self):
        (ret, patch_id) = self.upload_package()
        if ret is False:
            return False
        (ret, server_id) = self.tars_service.get_server_id(self.service_name)
        if ret is False:
            return False
        return self.tars_service.patch_tars(server_id, patch_id)
