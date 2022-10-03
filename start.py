import logging
import signal
import time
import os
import socket
import random

from getmac import get_mac_address as gma
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp

import constants
import util
import util_network as nu

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
        if constants.INTERFACE_TO_USE_KEY in args_dict:
            interface = args_dict[constants.INTERFACE_TO_USE_KEY]
        else:
            interface = "wlan0"
        LOG.debug("Interface <%s> used to expose MUD URL: <%s>", interface, args_dict[constants.MUD_URL_KEY])
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
    byte_mac_addr=nu.mac_to_bytes(MAC)
    x = bytearray(byte_mac_addr)
    x.insert(0, 1)
    x = bytes(x)
    hostname = socket.gethostname()
    device_IP = nu.get_ip()
    LOG.debug("%s --- IP: %s --- MAC address: %s", hostname, device_IP, MAC)

    # dhcp_options = [("message-type", "discover")]  ## Discover: The first message of a DHCP flow -> Can I have a DHCP address?
    dhcp_options = [("message-type", "request")]  ## Request: The third message of a DHCP flow -> I would like to accept your offer
    dhcp_options.append(("client_id", x))
    dhcp_options.append(("requested_addr", device_IP))
    dhcp_options.append(("hostname", hostname))
    dhcp_options.append(("mud-url", mud_url))
    dhcp_options.append("end")
    dhcp_object = DHCP(options=dhcp_options)
    packet = (
        Ether(dst="ff:ff:ff:ff:ff:ff") /
        IP(src="0.0.0.0", dst="255.255.255.255") /
        UDP(sport=68, dport=67) /
        BOOTP(
            chaddr=byte_mac_addr,
            xid=random.randint(1, 2**32-1),  # Random integer required by DHCP
        ) /
        dhcp_object
    )
    LOG.debug("Packet to send:\n %s", packet.__str__)
    x = sendp(packet, iface=interface_name, verbose=verbose, return_packets=True)

    LOG.debug("MUD URL Exposed!")

def execute_requests(addresses, waiting_time, download=False):
    for address in addresses:
        isOk = nu.ping(address)
        # LOG.info(f"The ping is: {isOk}")
        # if args_dict[constants.TRACEROUT_KEY]:
        #    nu.traceroute(address)
        if download:
            filename = os.path.basename(address)
            isOk = nu.curl(address, filename)
            if isOk:
                LOG.debug(f"File {filename} was succesfully downloaded")
        time.sleep(waiting_time)


if __name__ == '__main__':
    print(constants.STARTUP_MESSAGE)
    signal.signal(signal.SIGINT, util.simple_end_signal_handler)
    signal.signal(signal.SIGTERM, util.simple_end_signal_handler)
    main()
    print(constants.END_MESSAGE)
