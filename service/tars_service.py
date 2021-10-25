#!/usr/bin/python
# -*- coding: UTF-8 -*-
from common import utilities
from common.utilities import ServiceInfo
from requests_toolbelt import MultipartEncoder
import requests
import time
import os


class TarsService:
    'basic class to access the tars'

    def __init__(self, tars_url, tars_token, app_name, deploy_ip):
        self.tars_url = tars_url
        self.tars_token = tars_token
        self.deploy_ip = deploy_ip
        if self.tars_url.endswith('/') is False:
            self.tars_url = self.tars_url + '/'
        self.add_application_url = self.tars_url + 'api/add_application'
        self.deploy_service_url = self.tars_url + 'api/deploy_server'
        self.get_port_url = self.tars_url + 'api/auto_port'
        self.add_config_url = self.tars_url + 'api/add_config_file'
        self.update_config_url = self.tars_url + 'api/update_config_file'
        # upload and publish the package
        self.upload_package_url = self.tars_url + 'api/upload_patch_package'
        self.add_task_url = self.tars_url + 'api/add_task'
        self.get_server_list_url = self.tars_url + 'api/server_list'
        self.config_file_list_url = self.tars_url + 'api/config_file_list'

        self.app_name = app_name
        self.token_param = {'ticket': self.tars_token}

    def create_application(self):
        "create application"
        if self.app_exists() is True:
            utilities.log_error(
                "application %s already exists" % self.app_name)
            return False
        utilities.log_info("create application: %s" % self.app_name)
        request_data = {'f_name': self.app_name}
        response = requests.post(
            self.add_application_url, params=self.token_param, data=request_data)
        return TarsService.parse_response("create application " + self.app_name, response)

    def parse_response(operation, response):
        if response.status_code != 200:
            utilities.log_error("%s failed, error message: %s, error code: %d" %
                                (operation, response.content, response.status_code))
            return False
        result = response.json()
        error_msg = result['err_msg']
        if len(error_msg) > 0:
            utilities.log_error("%s failed, error message: %s" %
                                (operation, error_msg))
            return False
        return True

    def get_auto_port(self):
        # get the auto_port
        utilities.log_info("get the un-occuppied port")
        params = {"node_name": self.deploy_ip, "ticket": self.tars_token}
        response = requests.get(self.get_port_url, params=params)
        if TarsService.parse_response("get the un-occupied port", response) is False:
            return (False, 0)
        result = response.json()
        if 'data' not in result:
            utilities.log_error("get empty un-occupied port")
            return (False, 0)
        node_info = result['data']
        if len(node_info) <= 0:
            utilities.log_error("get empty un-occupied port")
            return (False, 0)
        if 'port' not in node_info[0]:
            utilities.log_error("get empty un-occupied port")
            return (False, 0)
        port = node_info[0]['port']
        utilities.log_info(
            "get the un-occupied port success, port: %s" % (port))
        return (True, int(port))

    def deploy_single_service(self, service_name, obj_name_list):
        "deploy single service"
        if self.server_exists(service_name) is True:
            utilities.log_error("service %s already exists." % service_name)
            return False
        utilities.log_info("deploy service %s" % service_name)
        adapters = []
        for obj_name in obj_name_list:
            # get the un-occupied port
            (ret, port) = self.get_auto_port()
            if ret is False:
                utilities.log_error(
                    "deploy service %s failed for get un-occupied port failed" % service_name)
                return False
            adapters.append({"obj_name": obj_name, "port": port, "bind_ip": self.deploy_ip, "port_type": "tcp",
                             "thread_num": 5, "max_connections": 100000, "queuecap": 50000, "queuetimeout": 20000})
        request_data = {"application": self.app_name, "server_name": service_name, "node_name": self.deploy_ip,
                        "server_type": "tars_cpp", "template_name": "tars.cpp.default", 'adapters': adapters}
        response = requests.post(
            self.deploy_service_url, params=self.token_param, json=request_data)
        if TarsService.parse_response("deploy service " + service_name, response) is False:
            return False
        return True

    def deploy_service_list(self, service_list, obj_list):
        "deploy service list"
        i = 0
        for service in service_list:
            if self.deploy_single_service(service, obj_list[i]) is False:
                utilities.log_error("deploy service list failed, service list: %s" %
                                    service_list)
                return False
            i = i + 1
        return True

    def get_level(server_name):
        # service level
        level = 5
        # app level
        if len(server_name) == 0:
            level = 1
        return level

    def add_config_file(self, config_file_name, server_name, config_file_path):
        "add the config file"
        utilities.log_info("add config file for application %s, config file path: %s" %
                           (self.app_name, config_file_path))
        try:
            fp = open(config_file_path)
            content = fp.read()
        except OSError as reason:
            utilities.log_error(
                "load the configuration failed, error: %s" % str(reason))
            return False

        request_data = {"level": TarsService.get_level(server_name), "application": self.app_name,
                        "server_name": server_name, "filename": config_file_name, "config": content}
        response = requests.post(
            self.add_config_url, params=self.token_param, json=request_data)
        if TarsService.parse_response("add application config file", response) is True:
            return True
        if response.status_code != 200:
            return False
        # try to update config
        utilities.log_info("add config file failed, try to update the config")
        return self.update_service_config(config_file_name, server_name, config_file_path)

    def update_service_config(self, config_file_name, server_name, config_file_path):
        utilities.log_info("update config file for application %s, config file path: %s" %
                           (self.app_name, config_file_path))
        ret, config_id = self.get_config_file_id(config_file_name, server_name)
        if ret is False:
            return False
        try:
            fp = open(config_file_path)
            content = fp.read()
        except OSError as reason:
            utilities.log_error(
                "load the configuration failed, error: %s" % str(reason))
        request_data = {"id": config_id, "config": content,
                        "reason": "update config file"}
        response = requests.post(
            self.update_config_url, params=self.token_param, json=request_data)
        if TarsService.parse_response("update config file for application " + self.app_name + ", config file:" + config_file_name, response) is False:
            return False
        return True

    def get_config_file_id(self, config_file_name, server_name):
        utilities.log_info("query the config file id for %s" %
                           config_file_name)

        params = {"ticket": self.tars_token, "level": TarsService.get_level(server_name), "application": self.app_name,
                  "server_name": server_name, "set_name": "", "set_area": "", "set_group": ""}
        response = requests.get(
            self.config_file_list_url, params=params)
        if TarsService.parse_response("query the config file id for " + config_file_name, response) is False:
            return (False, 0)
        result = response.json()
        if "data" not in result or len(result["data"]) == 0:
            utilities.log_error(
                "query the config file id failed for %s because of empty return data, response: %s" % (config_file_name, response.content))
            return (False, 0)
        # try to find the config file info
        for item in result["data"]:
            if "filename" in item and item["filename"] == config_file_name:
                return (True, item["id"])
        utilities.log_error("the config file %s not found" % config_file_name)
        return (False, 0)

    def add_config_list(self, config_list, service_name, config_file_list):
        i = 0
        for config_file_path in config_file_list:
            config = config_list[i]
            if self.add_config_file(config, service_name, config_file_path) is False:
                utilities.log_error("add_config_list failed, config files info: %s" %
                                    config_list)
            i = i+1
        return True

    def upload_tars_package(self, service_name, package_path):
        """
        upload the tars package
        """
        package_name = service_name + ServiceInfo.tars_pkg_postfix
        utilities.log_info("upload tars package for service %s, package_path: %s, package_name: %s" %
                           (service_name, package_path, package_name))
        if os.path.exists(package_path) is False:
            utilities.log_error("upload tars package for service %s failed for the path %s not exists" % (
                service_name, package_path))
            return (False, 0)
        form_data = MultipartEncoder(fields={"application": self.app_name, "module_name": service_name, "comment": "upload package", "suse": (
            package_name, open(package_path, 'rb'), 'text/plain/binary')})
        response = requests.post(self.upload_package_url, data=form_data, params=self.token_param, headers={
                                 'Content-Type': form_data.content_type})
        if TarsService.parse_response("upload tars package " + package_path, response) is False:
            return (False, 0)
        # get the id
        result = response.json()
        if 'data' not in result:
            utilities.log_error("upload tar package %s failed for empty return message: %s" %
                                (package_path, result))
            return (False, 0)
        result_data = result['data']
        if 'id' not in result_data:
            utilities.log_error("upload tar package %s failed for empty return message: %s" %
                                (package_path, result))
            return (False, 0)
        # Note: 11 is the tars services occupied id num
        id = result_data['id'] + 11
        return (True, id)

    def get_server_info(self, tree_node_id):
        params = {'tree_node_id': tree_node_id, "ticket": self.tars_token}
        response = requests.get(self.get_server_list_url, params=params)
        if TarsService.parse_response("get server info by tree node id: " + tree_node_id, response) is False:
            utilities.log_error("get server info by tree node id for error response, tree_node_id: %s, msg: %s" % (
                tree_node_id, response.content))
            return (False, response)
        return (True, response)

    def app_exists(self):
        (ret, response) = self.get_server_info("1" + self.app_name)
        if ret is False:
            return False
        result = response.json()
        if 'data' in result and len(result["data"]) > 0:
            return True
        return False

    def server_exists(self, service_name):
        node_tree_id = "1" + self.app_name + ".5" + service_name
        (ret, response) = self.get_server_info(node_tree_id)
        if ret is False:
            return False
        result = response.json()
        if 'data' in result and len(result["data"]) > 0:
            return True
        return False

    def get_server_id(self, service_name):
        # tree_node_id
        tree_node_id = "1" + self.app_name + ".5" + service_name
        (ret, response) = self.get_server_info(tree_node_id)
        if ret is False:
            return (False, 0)
        if TarsService.parse_response("get server list ", response) is False:
            utilities.log_error("get server info failed for error response, server name: %s, msg: %s" % (
                service_name, response.content))
            return (False, 0)
        result = response.json()
        if "data" not in result or len(result["data"]) == 0 or "id" not in result["data"][0]:
            utilities.log_error("get server info failed for empty return, server name: %s" %
                                service_name)
            return (False, 0)
        server_id = result["data"][0]["id"]
        return (True, server_id)

    def upload_and_publish_package(self, service_name, package_path):
        """
        upload and publish the tars package
        """
        # get the service info
        (ret, server_id) = self.get_server_id(service_name)
        if ret is False:
            utilities.log_error(
                "upload and publish package failed for get the server info failed, server: %s" % service_name)
            return False
        # upload the tars package
        (ret, patch_id) = self.upload_tars_package(service_name, package_path)
        if ret is False:
            return False
        # patch tars
        self.patch_tars(server_id, patch_id)
        return True

    def patch_tars(self, server_id, patch_id):
        utilities.log_info("patch tars for application %s, server_id: %s, patch_id: %s" % (
            self.app_name, server_id, patch_id))
        items = [{"server_id": server_id, "command": "patch_tars", "parameters": {
            "patch_id": patch_id, "bak_flag": 'false', "update_text": "", "group_name": ""}}]
        request_data = {"serial": 'true', "items": items}
        response = requests.post(
            self.add_task_url, params=self.token_param, json=request_data)
        if TarsService.parse_response("patch tars ", response) is False:
            utilities.log_error("patch tars failed for error response, server id: %s, msg: %s" % (
                server_id, response.content))
            return False
        utilities.log_info("patch tars response %s" % response.content)
        return True

    def add_task(self, service_name, command):
        """
        current supported commands are: stop, restart, undeploy_tars, patch_tars
        """
        utilities.log_info("add_task for service %s, command is %s" %
                           (service_name, command))
        (ret, server_id) = self.get_server_id(service_name)
        if ret is False:
            return False
        items = [{"server_id": server_id, "command": command, "parameters": {}}]
        request_data = {"serial": 'true', "items": items}
        response = requests.post(
            self.add_task_url, params=self.token_param, json=request_data)
        if TarsService.parse_response("execute command " + command, response) is False:
            utilities.log_error("add_task failed for error response, server name: %s, msg: %s" % (
                service_name, response.content))
            return False
        return True

    def stop_server(self, service_name):
        """
        stop the givn service
        """
        return self.add_task(service_name, "stop")

    def stop_server_list(self, server_list):
        for server in server_list:
            if self.stop_server(server) is False:
                return False
        return True

    def restart_server(self, service_name):
        """
        restart the given service
        """
        return self.add_task(service_name, "restart")

    def undeploy_tars(self, service_name):
        """
        undeploy the tars service
        """
        return self.add_task(service_name, "undeploy_tars")

    def undeploy_server_list(self, server_list):
        for server in server_list:
            if self.undeploy_tars(server) is False:
                return False
        return True

    def restart_server_list(self, server_list):
        for server in server_list:
            if self.restart_server(server) is False:
                return False
            time.sleep(5)
        return True

    def get_service_list(self):
        return self.get_server_info("1" + self.app_name)

    def upload_and_publish_package_list(self, service_list, service_path_list):
        i = 0
        for service in service_list:
            service_path = service_path_list[i]
            self.upload_and_publish_package(service, service_path)
            i = i+1
            time.sleep(10)
