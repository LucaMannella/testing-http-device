import socket
import json
import logging
import sys
import argparse
from datetime import datetime
from typing import Union

import constants


def simple_end_signal_handler(signal, frame):
    """ Function to be used as signal handler for SIGINT or SIGTERM.
        It only print an information and close the Python application.
    """

    print("\nInterrupt received, shutting down the program...\n")
    sys.exit(0)


def init_logger(log_name: str, debug_level: Union[int, str]):
    """ This function configure the logger according to the specified debug_level taken from logging class. """
    # logging.basicConfig(format="%(message)s")

    logger = logging.getLogger(log_name)
    logger.setLevel(level=debug_level)
    
    formatter = logging.Formatter(constants.DEFAULT_LOG_FORMATTER, datefmt="(%b-%d) %H:%M:%S")
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    
    return logger


def parse_json_file(filename: str) -> dict:
    """ Read a JSON file and return a JSON object with the related data.

        :param filename: the full-path of the configuration file.
        :return: a Dictionary containing the configuration data.
    """

    file_p = open(filename)
    if file_p:
        content_json = json.load(file_p)
        file_p.close()
        return content_json
    else:
        raise FileNotFoundError("File: "+filename+" not found or you don't have permission to read it!")


def parse_config_file(app_name: str, description: str) -> dict:
    """ This function retrieve a filename from command line and retrieve the desired data.

    :return: an object with all the parsed parameters.
    """
    example_text = "example: start_mqtt_client.py -c config/config.json"

    parser = argparse.ArgumentParser(prog=app_name, description=description, epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config', default=constants.DEFAULT_CONFIG, type=str,
                        help='the name of the desired preference file')
    cmd_line = parser.parse_args()
    config_file = cmd_line.config
    args_dict = parse_json_file(config_file)
    return args_dict

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1)) # doesn't even have to be reachable
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def mac_to_bytes(mac_addr: str) -> bytes:
    """ Converts a MAC address string to bytes. """
    return int(mac_addr.replace(":", ""), 16).to_bytes(6, "big")
