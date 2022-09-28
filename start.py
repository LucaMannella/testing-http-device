import logging
import signal
import time
from datetime import datetime
import os
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

import constants
import util


def main():
    # 0) Parsing command line and configuration file
    description_text = "This app sends HTTP requests"
    args_dict = util.parse_config_file(constants.SIMULATOR_APP_NAME, description_text)

    # 1) Logging initialization
    try:
        if args_dict[constants.VERBOSE_KEY]:
            logging_level = logging.DEBUG
            verbose = True
        else:
            logging_level = logging.INFO
            verbose = False
    except KeyError:
        logging_level = logging.INFO

    util.init_logger(logging_level)
    logging.debug("Verbose mode enabled")  # Printed only if logging_level is DEBUG

    # 2) Retrieving necessary values
    addresses = args_dict[constants.CONNECTING_ADDRESSES_KEY]
    logging.debug(f"Connecting to {len(addresses)} urls")
    counter = 0
    for a in addresses:
        counter += 1
        logging.debug(f"{counter}. {a}")
    time.sleep(1)

    # 3) Sending requests
    execute_requests(addresses, args_dict[constants.TIME_AMONG_REQUESTS_KEY], args_dict[constants.DOWNLOAD_KEY])

    # Sending requests forever if required
    waiting_interval = args_dict[constants.TIME_AMONG_BURSTS_KEY]
    infinite_loop = args_dict[constants.INFINITE_REQUESTS_KEY]
    while(infinite_loop):
        time.sleep(waiting_interval)
        execute_requests(addresses, args_dict[constants.TIME_AMONG_REQUESTS_KEY], args_dict[constants.DOWNLOAD_KEY])


def execute_requests(addresses, waiting_time, download=False):
    for address in addresses:
        isOk = ping(address)
        # logging.info(f"The ping is: {isOk}")
        # if args_dict[constants.TRACEROUT_KEY]:
        #    traceroute(address)
        if download:
            filename = os.path.basename(address)
            isOk = curl(address, filename)
            if isOk:
                logging.debug(f"File {filename} was succesfully downloaded")
        time.sleep(waiting_time)


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0
    
def traceroute(host):
    param = '-m 3'  # number of hops
    command = ['traceroute', param, host]
    return subprocess.call(command) == 0

def curl(host, filename):
    param = '-o '+filename
    command = ["curl", param, host]
    return subprocess.call(command) == 0


if __name__ == '__main__':
    print(constants.STARTUP_MESSAGE)
    signal.signal(signal.SIGINT, util.simple_end_signal_handler)
    signal.signal(signal.SIGTERM, util.simple_end_signal_handler)
    main()
    print(constants.END_MESSAGE)
