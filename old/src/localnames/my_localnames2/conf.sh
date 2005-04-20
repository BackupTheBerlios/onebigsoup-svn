# BASH


#  !!! CHANGE THIS TO "1" !!!
#
READY_TO_INSTALL="1"


# BASH & PYTHON: - where are they?
BASH="/bin/bash"
PYTHON="/usr/bin/python2.3"

# TARGET: where CGI scripts, Python scripts, user data,
#         will be stored
TARGET="/var/www/testing.taoriver.net"

# CHOWN_TO: the user and group that all
#           installed files should belong to
CHOWN_TO="lion.lionsweb"

# XMLRPC_LN_SERVER:  URL of XML-RPC LocalNames resolving server;
#                    feel free to use Lion's until you get your
#                    own up and running
XMLRPC_LN_SERVER="http://services.taoriver.net:9089/"

# URL_DOMAIN_NAME:  Domain name or IP addressed used in URL
#                   to access my.localnames.
URL_DOMAIN_NAME="testing.taoriver.net"

# URL_DIRECTORY_BASE:  Base of URL used to access my.localnames.
#                      ex:  URL_DIRECTORY_BASE="/testing/"
URL_DIRECTORY_BASE="/"


# TMP:  Safe directory for temporary data;
#       "Safe" defined as "nukable, but usable for a few
#       seconds here and there."
TMP="/tmp"


###########################################
#  DO NOT CHANGE anything below this line #
###########################################

CONF_VERSION="1"


