#!/usr/bin/python
# -*- coding: UTF-8 -*-
from common import utilities
from common.utilities import ServiceInfo


class TarsConfig:
    def __init__(self, config):
        self.config = config
        section = "tars"
        self.tars_url = utilities.get_value(
            self.config, section, "tars_url", None, True)
        self.tars_token = utilities.get_value(
            self.config, section, "tars_token", None, True)
        self.tars_pkg_dir = utilities.get_value(
            self.config, section, "tars_pkg_dir", "../build", False)


class ServiceInfoConfig:
    def __init__(self, config, chain_id):
        self.config = config
        self.name = utilities.get_item_value(self.config,
                                             "name", chain_id, False)
        self.deploy_ip = utilities.get_item_value(
            self.config, "deploy_ip", None, True)
        self.listen_ip = utilities.get_item_value(
            self.config, "listen_ip", ServiceInfo.default_listen_ip, False)
        self.listen_port = utilities.get_item_value(
            self.config, "listen_port", 20200, False)
        self.thread_count = utilities.get_item_value(
            self.config, "thread_count", 4, False)


class RpcServiceInfo(ServiceInfoConfig):
    def __init__(self, config, chain_id):
        ServiceInfoConfig.__init__(self, config, chain_id)
        self.rpc_service_name = utilities.get_item_value(
            self.config, "rpc_service_name", self.name, False)
        self.gateway_service_name = utilities.get_item_value(
            self.config, "gateway_service_name", None, True)
        self.peers = []


class GatewayServiceInfo(ServiceInfoConfig):
    def __init__(self, config, chain_id):
        ServiceInfoConfig.__init__(self, config, chain_id)
        self.peers = utilities.get_item_value(
            self.config, "peers", [], False)
        self.rpc_service_name = utilities.get_item_value(
            self.config, "rpc_service_name", None, True)
        self.gateway_service_name = utilities.get_item_value(
            self.config, "gateway_service_name", self.name, False)


class NodeConfig:
    def __init__(self, config, group_id, chain_id, index):
        self.config = config
        self.group_id = group_id
        self.chain_id = chain_id
        self.node_count = utilities.get_item_value(
            self.config, "node_count", 1, False)
        self.deploy_ip = utilities.get_item_value(
            self.config, "deploy_ip", None, True)
        self.rpc_service_name = utilities.get_item_value(
            self.config, "rpc_service_name", None, True)
        self.gateway_service_name = utilities.get_item_value(
            self.config, "gateway_service_name", None, True)
        self.microservice_node = utilities.get_item_value(
            self.config, "microservice_node", False, False)
        self.obj_name_list = []
        self.node_name = utilities.get_item_value(
            self.config, "node_name", "node" + str(index), False)
        self.service_list = {}
        if self.microservice_node is False:
            self.service_list[ServiceInfo.single_node_service] = self.deploy_ip
            self.obj_name_list = ServiceInfo.single_node_obj_name_list
        else:
            service_list = utilities.get_item_value(
                self.config, "service_list", None, False)
            if service_list is not None:
                self.service_list = eval(service_list)
                for service in ServiceInfo.micro_node_service:
                    if service not in self.service_list:
                        self.service_list[service] = self.deploy_ip
            if service_list is None:
                for service in ServiceInfo.micro_node_service:
                    self.service_list[service] = self.deploy_ip
        utilities.log_info("the service info: %s" % str(self.service_list))
        self.generate_service_name_list()
        self.generate_service_config_info()

    def get_node_name(self, index):
        return self.node_name + str(index)

    def get_service_name(self, index, service):
        return self.group_id + self.get_node_name(index) + service

    def get_single_node_service_name(self, index):
        services = {}
        for service in self.service_list.keys():
            services[self.get_service_name(index, service)] = service
        return services

    def generate_service_name_list(self):
        self.nodes_service_name_list = {}
        for i in range(0, self.node_count):
            node_service_info = self.get_single_node_service_name(i)
            self.nodes_service_name_list[self.get_node_name(
                i)] = node_service_info
        utilities.log_info("generate service name list: %s" %
                           str(self.nodes_service_name_list))

    def generate_service_config_info(self):
        self.node_service_config_info = {}
        for i in range(0, self.node_count):
            node_service_config_item = {}
            node_name = self.get_node_name(i)
            for config_key in ServiceInfo.micro_node_service_config_keys.keys():
                node_service_config_item[config_key] = node_name + \
                    ServiceInfo.micro_node_service_config_keys[config_key]
            self.node_service_config_info[node_name] = node_service_config_item
        utilities.log_info("generate service config info: %s" %
                           str(self.node_service_config_info))


class GenesisConfig:
    def __init__(self, config):
        self.config = config
        section = "group"
        self.leader_period = utilities.get_value(
            self.config, section, "leader_period", 1, False)
        self.block_tx_count_limit = utilities.get_value(
            self.config, section, "block_tx_count_limit", 1000, False)
        self.consensus_timeout = utilities.get_value(
            self.config, section, "consensus_timeout", 3000, False)
        self.consensus_type = utilities.get_value(
            self.config, section, "consensus_type", "pbft", False)
        self.gas_limit = utilities.get_value(
            self.config, section, "gas_limit", "300000000", False)


class GroupConfig:
    def __init__(self, config, chain_id):
        self.config = config
        self.chain_id = chain_id
        self.section = "group"
        self.group_id = utilities.get_value(
            self.config, self.section, "group_id", "group", False)
        self.vm_type = utilities.get_value(
            self.config, self.section, "vm_type", "evm", False)
        self.sm_crypto = utilities.get_value(
            self.config, self.section, "sm_crypto", False, False)
        self.genesis_config = GenesisConfig(self.config)
        self.parse_node_config()

    def parse_node_config(self):
        self.node_list = []
        node_config_list = utilities.get_value(
            self.config, self.section, "deploy_info", [], False)
        i = 0
        for item in node_config_list:
            self.node_list.append(NodeConfig(
                item, self.group_id, self.chain_id, i))
            i = i + 1


class ChainConfig:
    def __init__(self, config):
        self.config = config
        self.chain_id = utilities.get_value(
            self.config, "chain", "chain_id", "chain0", False)
        self.ca_cert_path = utilities.get_value(
            self.config, "chain", "ca_cert_path", "", False)
        self.tars_config = TarsConfig(config)
        self.rpc_config = self.parse_service_config(
            "rpc", self.chain_id, "RpcServiceInfo")
        self.gateway_config = self.parse_service_config(
            "gateway", self.chain_id, "GatewayServiceInfo")
        self.group_config = GroupConfig(
            config, self.chain_id)
        self.rpc_sm_ssl = utilities.get_value(
            self.config, "chain", "rpc_sm_ssl", False, False)
        self.gateway_sm_ssl = utilities.get_value(
            self.config, "chain", "gateway_sm_ssl", False, False)

    def parse_service_config(self, section_name, chain_id, constructor):
        service_list = utilities.get_value(
            self.config, "chain", section_name, [], False)
        result = {}
        for item in service_list:
            function = "%s(item, chain_id)" % constructor
            service_object = eval(function)
            result[service_object.name] = service_object
        return result
