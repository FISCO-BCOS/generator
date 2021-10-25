#!/usr/bin/python
# -*- coding: UTF-8 -*-
import configparser
from common import utilities
from common.utilities import ServiceInfo
from common.utilities import ConfigInfo
import json
import os


class ServiceConfigGenerator:
    def __init__(self, config, service_type):
        self.config = config
        self.ini_file = "config.ini"
        self.ini_tmp_file = "config.ini.tmp"
        self.network_file = "nodes.json"
        self.network_tmp_file = "nodes.json.tmp"
        self.service_type = service_type
        self.init(service_type)

    def init(self, service_type):
        self.config_file_list = []
        self.config_path_list = []
        if service_type == ServiceInfo.rpc_service_type:
            self.root_dir = "rpc"
            self.section = "rpc"
            self.service_config = self.config.rpc_config
            self.tpl_config_path = ConfigInfo.rpc_config_tpl_path
        if service_type == ServiceInfo.gateway_service_type:
            self.root_dir = "gateway"
            self.section = "p2p"
            self.service_config = self.config.gateway_config
            self.tpl_config_path = ConfigInfo.gateway_config_tpl_path
            (connect_file, connect_file_path) = self.get_network_connection_config_info()
            self.config_file_list.append(connect_file)
            self.config_path_list.append(connect_file_path)
        (file_list, path_list) = self.get_cert_config_info()
        self.config_file_list.extend(file_list)
        self.config_path_list.extend(path_list)

        (ini_file, ini_path) = self.get_ini_config_info()
        self.config_file_list.append(ini_file)
        self.config_path_list.append(ini_path)

    def generate_all_config(self):
        if self.service_type == ServiceInfo.gateway_service_type:
            self.generate_gateway_config_files()
        else:
            self.generate_rpc_config_files()
        return True

    def generate_rpc_config_files(self):
        self.generate_ini_config()
        self.generate_cert()

    def generate_gateway_config_files(self):
        self.generate_ini_config()
        self.generate_cert()
        self.generate_gateway_connection_info()

    def get_ini_config_info(self):
        config_path = os.path.join(
            self.root_dir, self.config.chain_id, self.service_config.name, self.ini_tmp_file)
        return (self.ini_file, config_path)

    def get_network_connection_config_info(self):
        config_path = os.path.join(self.root_dir, self.config.chain_id,
                                   self.config.gateway_config.name, self.network_tmp_file)
        return (self.network_file, config_path)

    def get_cert_output_dir(self):
        return os.path.join(self.root_dir, self.config.chain_id, self.service_config.deploy_ip)

    def generate_ini_config(self):
        """
        generate config.ini.tmp
        """
        ini_config = configparser.ConfigParser()
        ini_config.read(self.tpl_config_path)
        ini_config[self.section]['listen_ip'] = self.service_config.listen_ip
        ini_config[self.section]['listen_port'] = str(
            self.service_config.listen_port)
        ini_config[self.section]['sm_ssl'] = utilities.convert_bool_to_str(
            self.service_config.sm_ssl)
        ini_config[self.section]['thread_count'] = str(
            self.service_config.thread_count)
        ini_config["service"]['gateway'] = self.config.gateway_config.name + \
            "." + ServiceInfo.gateway_service
        ini_config["service"]['rpc'] = self.config.rpc_config.name + \
            "." + ServiceInfo.rpc_service
        ini_config["chain"]['chain_id'] = self.config.chain_id
        (_, generated_file_path) = self.get_ini_config_info()
        utilities.mkfiledir(generated_file_path)
        with open(generated_file_path, 'w') as configfile:
            ini_config.write(configfile)

    def generate_gateway_connection_info(self):
        peers = {}
        peers["nodes"] = self.config.gateway_config.peers
        (_, generated_file_path) = self.get_network_connection_config_info()
        utilities.mkfiledir(generated_file_path)
        with open(generated_file_path, 'w') as configfile:
            json.dump(peers, configfile)

    def generate_cert_with_command(self, command):
        """
        generate cert for the network
        """
        output_dir = self.get_cert_output_dir()
        utilities.generate_cert_with_command(
            self.service_config.sm_ssl, command, output_dir)

    def generate_cert(self):
        return self.generate_cert_with_command("generate_cert")

    def get_cert_config_info(self):
        ssl_config_files = ServiceInfo.ssl_file_list
        if self.service_config.sm_ssl is True:
            ssl_config_files = ServiceInfo.sm_ssl_file_list
        generated_file_paths = []
        for item in ssl_config_files:
            output_dir = self.get_cert_output_dir()
            generated_file_paths.append(os.path.join(output_dir, "ssl", item))
        return (ssl_config_files, generated_file_paths)
