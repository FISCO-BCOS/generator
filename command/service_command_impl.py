#!/usr/bin/python
# -*- coding: UTF-8 -*-
from controller.service_controller import ServiceController


class ServiceCommandImpl:
    def __init__(self, config, service_type):
        self.config = config
        self.service_type = service_type
        self.service_controller = ServiceController(config, service_type)

    def gen_service_config(self):
        return self.service_controller.config_generator.generate_all_config()

    def upload_service(self):
        # upload the generated_config
        return self.service_controller.deploy_service()

    def deploy_service(self):
        # generate_config
        self.service_controller.config_generator.generate_all_config()
        return self.service_controller.deploy_service()

    def delete_service(self):
        return self.service_controller.undeploy_service()

    def upgrade_service(self):
        return self.service_controller.upgrade_service()

    def start_service(self):
        return self.service_controller.start_service()

    def stop_service(self):
        return self.service_controller.stop_service()
