#!/usr/bin/python
# -*- coding: UTF-8 -*-
from controller.service_controller import ServiceController


class ServiceCommandImpl:
    def __init__(self, config, service_type):
        self.config = config
        self.service_type = service_type
        self.service_controller = ServiceController(config, service_type)

    def gen_service_config(self):
        return self.service_controller.gen_all_service_config()

    def upload_service(self):
        # upload the generated_config
        return self.service_controller.deploy_all()

    def deploy_service(self):
        # generate_config
        self.gen_service_config()
        return self.service_controller.deploy_all()

    def delete_service(self):
        return self.service_controller.undeploy_all()

    def upgrade_service(self):
        return self.service_controller.upgrade_all()

    def start_service(self):
        return self.service_controller.start_all()

    def stop_service(self):
        return self.service_controller.stop_all()
