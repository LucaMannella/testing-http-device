import logging
import signal
import time
from datetime import datetime
import os
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import socket
import random

from getmac import get_mac_address as gma
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp

import constants
import util

LOG = None

def main():
    # 0) Parsing command line and configuration file
    args_dict = util.parse_config_file(constants.APP_NAME, constants.DESCRIPTION_TEXT)

    # 1) Logging initialization
    try:
        if args_dict[constants.VERBOSE_KEY]:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
    except KeyError:
        logging_level = logging.INFO

    global LOG
    LOG = util.init_logger(constants.APP_NAME, logging_level)
    LOG.debug("Verbose mode enabled")  # Printed only if logging_level is DEBUG

    # 2) Retrieving necessary values
    addresses = args_dict[constants.CONNECTING_ADDRESSES_KEY]
    LOG.debug(f"Connecting to {len(addresses)} urls")
    counter = 0
    for a in addresses:
        counter += 1
        LOG.debug(f"{counter}. {a}")
    time.sleep(1)

    # 3 opt) if available exposing MUD URL
    if constants.MUD_URL_KEY in args_dict:
        LOG.debug("MUD URL to expose: <%s>", args_dict[constants.MUD_URL_KEY])
        if constants.INTERFACE_TO_USE_KEY in args_dict:
            interface = args_dict[constants.INTERFACE_TO_USE_KEY]
        else:
            interface = "wlan0"
        expose_mud_url(args_dict[constants.MUD_URL_KEY], interface)

    # 4) Sending requests
    execute_requests(addresses, args_dict[constants.TIME_AMONG_REQUESTS_KEY], args_dict[constants.DOWNLOAD_KEY])

    # Sending requests forever if required
    waiting_interval = args_dict[constants.TIME_AMONG_BURSTS_KEY]
    infinite_loop = args_dict[constants.INFINITE_REQUESTS_KEY]
    while(infinite_loop):
        time.sleep(waiting_interval)
        execute_requests(addresses, args_dict[constants.TIME_AMONG_REQUESTS_KEY], args_dict[constants.DOWNLOAD_KEY])

def expose_mud_url(mud_url, interface_name="wlan0", verbose=True):
    MAC = gma()
    hostname = socket.gethostname()
    device_IP = socket.gethostbyname(hostname)
    LOG.debug("%s --- IP: %s --- MAC address: %s", hostname, device_IP, MAC)

    LOG.debug("Trying to expose the MUD URL: %s", mud_url)
    packet = (
        Ether(dst="ff:ff:ff:ff:ff:ff") /
        IP(src=device_IP, dst="255.255.255.255") /
        UDP(sport=68, dport=67) /
        BOOTP(
            chaddr=util.mac_to_bytes(MAC),
            xid=random.randint(1, 2**32-1),  # Random integer required by DHCP
        ) /
        # DHCP(options=[("message-type", "discover"), "end"])
        DHCP(options=[("message-type", "discover"), ("mud-url", mud_url), "end"])
    )
    LOG.debug("Packet to send:\n %s", packet.__str__)
    x = sendp(packet, iface=interface_name, verbose=verbose, return_packets=True)

    LOG.debug("MUD URL Exposed!")

def execute_requests(addresses, waiting_time, download=False):
    for address in addresses:
        isOk = ping(address)
        # LOG.info(f"The ping is: {isOk}")
        # if args_dict[constants.TRACEROUT_KEY]:
        #    traceroute(address)
        if download:
            filename = os.path.basename(address)
            isOk = curl(address, filename)
            if isOk:
                LOG.debug(f"File {filename} was succesfully downloaded")
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
