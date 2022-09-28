# Printed strings
STARTUP_MESSAGE = "\nThis application will send several ICMP or HTTP requests.\n"
END_MESSAGE = "\nAll the requests were executed.\n"

# Default values
DEFAULT_CONFIG = "config/config.json"
DEFAULT_KEEPALIVE = 60

# Configuration parameter keys
CONNECTING_ADDRESSES_KEY = "connecting_addresses"
TIME_AMONG_REQUESTS_KEY = "time_s_among_requests"
TIME_AMONG_BURSTS_KEY = "time_s_among_bursts"
VERBOSE_KEY = "verbose"
TRACEROUT_KEY = "traceroute"
DOWNLOAD_KEY = "download"
INFINITE_REQUESTS_KEY = "infinite_requests"
MUD_URL_KEY = "mud_url"

# log
DEFAULT_LOG_FORMATTER = "%(asctime)s.%(msecs)04d %(name)-7s %(levelname)s: %(message)s"
RFC3339_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
APP_NAME = "Fake-HTTP-Device"
DESCRIPTION_TEXT = "This app sends HTTP requests"

# Other
NO_VALUE = "-----"
