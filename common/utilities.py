#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import subprocess


class ServiceInfo:
    rpc_service_type = "rpc"
    gateway_service_type = "gateway"

    ssl_file_list = ["ca.crt", "ssl.key", "ssl.crt"]
    sm_ssl_file_list = ["sm_ca.crt", "sm_ssl.key", "sm_ssl.crt", "sm_enssl.key", "sm_enssl.crt"]

    rpc_service = "RpcService"
    gateway_service = "GatewayService"

    single_node_service = "NativeNode"
    single_node_obj_name_list = [
        "LedgerServiceObj", "SchedulerServiceObj", "TxPoolServiceObj", "PBFTServiceObj", "FrontServiceObj"]
    micro_node_service = ["TxPoolService",
                          "FrontService", "SchedulerService", "PBFTService", "ExecutorService"]
    micro_node_service_config_keys = {"txpool": "TxPoolService", "front": "FrontService",
                                      "scheduler": "SchedulerService", "consensus": "PBFTService", "executor": "ExecutorService"}

    supported_vm_types = ["evm", "wasm"]
    supported_consensus_list = ["pbft"]
    tars_pkg_postfix = ".tgz"
    default_listen_ip = "0.0.0.0"
    cert_generationscript_path = "scripts/generate_cert.sh"


class ConfigInfo:
    tpl_abs_path = "tpl/"
    pwd_path = os.getcwd()
    rpc_config_tpl_path = os.path.join(
        pwd_path, tpl_abs_path, "config.ini.rpc")
    gateway_config_tpl_path = os.path.join(
        pwd_path, tpl_abs_path, "config.ini.gateway")
    genesis_config_tpl_path = os.path.join(
        pwd_path, tpl_abs_path, "config.genesis")
    node_config_tpl_path = os.path.join(
        pwd_path, tpl_abs_path, "config.ini.node")


class CommandInfo:
    node_command = ["gen_node_config", "start_all",
                    "stop_all", "deploy_nodes", "upgrade_nodes", "upload_nodes", "undeploy_nodes"]
    service_command = ["gen_service_config", "start_service", "stop_service",
                       "upload_service", "deploy_service", "delete_service", "upgrade_service"]
    total_command = node_command + service_command


def log_error(error_msg):
    print("\033[31m%s \033[0m" % error_msg)


def log_info(error_msg):
    print("\033[32m%s \033[0m" % error_msg)


def get_item_value(config, key, default_value, must_exist):
    if key in config:
        return config[key]
    if must_exist:
        raise Exception("the value for deploy_info.%s must be set" % key)
    return default_value


def get_value(config, section, key, default_value, must_exist):
    if section in config and key in config[section]:
        return config[section][key]
    if must_exist:
        raise Exception("the value for deploy_info.%s must be set" % key)
    return default_value


def execute_command(command):
    status, output = subprocess.getstatusoutput(command)
    if status != 0:
        log_error(
            "execute command %s failed, error message: %s" % (command, output))
        return False
    log_info("execute command %s success" % command)
    return True


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def mkfiledir(filepath):
    parent_dir = os.path.abspath(os.path.join(filepath, ".."))
    mkdir(parent_dir)


def generate_service_name(prefix, service_name):
    return prefix + service_name


def convert_bool_to_str(value):
    if value is True:
        return "true"
    return "false"


def generate_cert_with_command(sm_type, command, outputdir, ca_cert_info):
    """
    generate cert for the network
    """
    sm_mode = ""
    if sm_type is True:
        sm_mode = " -s"
    generate_cert_cmd = "bash %s -o %s -c %s %s %s" % (
        ServiceInfo.cert_generationscript_path, outputdir, command, sm_mode, ca_cert_info)
    if execute_command(generate_cert_cmd) is False:
        log_error("%s failed" % command)
        sys.exit(0)


def generate_private_key(sm_type, outputdir):
    generate_cert_with_command(sm_type, "generate_private_key", outputdir, "")


def generate_cert(sm_type, outputdir):
    generate_cert_with_command(sm_type, "generate_all_cert", outputdir, "")


def generate_ca_cert(sm_type, outputdir):
    command = "generate_ca_cert"
    generate_cert_with_command(sm_type, command, outputdir, "")


def generate_node_cert(sm_type, ca_cert_path, outputdir):
    command = "generate_node_cert"
    ca_cert_info = "-d %s" % ca_cert_path
    generate_cert_with_command(sm_type, command, outputdir, ca_cert_info)

def generate_sdk_cert(sm_type, ca_cert_path, outputdir):
    command = "generate_sdk_cert"
    ca_cert_info = "-d %s" % ca_cert_path
    generate_cert_with_command(sm_type, command, outputdir, ca_cert_info)

def try_to_rename_tgz_package(tars_pkg_path, service_name, org_service_name):
    org_package_name = org_service_name + ServiceInfo.tars_pkg_postfix
    org_package_path = os.path.join(tars_pkg_path, org_package_name)
    unzip_binary_path = os.path.join("./", org_service_name, org_service_name)
    if service_name == org_service_name:
        return (True, org_package_path)
    renamed_package_name = service_name + ServiceInfo.tars_pkg_postfix
    renamed_package_path = os.path.join("./", renamed_package_name)
    renamed_binary_path = os.path.join("./", service_name, service_name)

    mkdir_command = "mkdir -p %s" % os.path.join("./", service_name)
    unzip_command = "tar -xvf %s" % org_package_path
    mv_command = "mv %s %s" % (unzip_binary_path, renamed_binary_path)
    zip_command = "tar -cvzf %s %s" % (renamed_package_path,
                                       renamed_binary_path)
    command = "%s && %s && %s && %s" % (
        mkdir_command, unzip_command, mv_command, zip_command)
    ret = execute_command(command)
    if ret is False:
        log_error("try_to_rename_tgz_package failed, service: %s" %
                  service_name)
    return (ret, renamed_package_path)
