#!/usr/bin/python
# -*- coding: UTF-8 -*-
import argparse
import toml
import ast
import sys

from common import utilities
from common.utilities import CommandInfo
from common.utilities import ServiceInfo
from config.chain_config import ChainConfig
from command.service_command_impl import ServiceCommandImpl
from command.node_command_impl import NodeCommandImpl


def parse_command():
    parser = argparse.ArgumentParser(description='build_chain')
    parser.add_argument(
        '--command', help="[required]the command, support " + ', '.join(CommandInfo.total_command), required=True)
    parser.add_argument(
        "--config", help="[optional] the config file, default is config.toml", default="config.toml")
    parser.add_argument("--type",
                        help="the service type, now support " + ServiceInfo.rpc_service_type + " and " +
                             ServiceInfo.gateway_service_type, required=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_command()
    toml_config = toml.load(args.config)
    chain_config = ChainConfig(toml_config)
    if args.command in CommandInfo.service_command:
        if args.type != ServiceInfo.rpc_service_type and args.type != ServiceInfo.gateway_service_type:
            utilities.log_error("the service type must be " +
                                ServiceInfo.rpc_service_type + " or " + ServiceInfo.gateway_service_type)
            return
        else:
            command_impl = ServiceCommandImpl(chain_config, args.type)
            cmd_func_attr = getattr(command_impl, args.command)
            ret = cmd_func_attr()
            if ret is True:
                utilities.log_info(args.command + " success!")
            return
    if args.command in CommandInfo.node_command:
        command_impl = NodeCommandImpl(chain_config)
        cmd_func_attr = getattr(command_impl, args.command)
        cmd_func_attr()
        return
    utilities.log_info("unimplemented command")


if __name__ == "__main__":
    main()
