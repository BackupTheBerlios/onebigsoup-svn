#
# conftests.sh
#
# (c) 2004 Lion Kimbro - released into public domain
#
#
# How to run:
#
#    $ ./conftests.sh
#
# How to include:
#
#    . ./conftests.sh
#
#
# this:
#   * performs basic configuration sanity checks
#   * relies on "conf.sh"
#
#
# environment variables:
#   * MY_LOCALNAMES_CONF_FILE,
#       - default: "./conf.sh"
#       - can set to say where to find configuration file
#     ex:
#       export MY_LOCALNAMES_CONF_FILE="/home/lion/my.localnames.conf.sh"
#
#
# SEE ALSO:
#   * install.sh
#   * uninstall.sh
#


SUCCESS="0"
ERROR_NO_CONF_SH="1"
ERROR_WRONG_VERSION_CONF_SH="2"
ERROR_UNCONFIGURED="3"
ERROR_NEEDED_FILE_NOT_FOUND="4"
ERROR_NO_TARGET="5"
ERROR_CANNOT_WRITE_IN_TARGET="6"
ERROR_CANNOT_DELETE_IN_TARGET="7"


########################################
# CONF FILE
########################################

if [[ "$MY_LOCALNAMES_CONF_FILE" == "" ]] ; then
    CONF_FILE="./conf.sh"
else
    CONF_FILE="$MY_LOCALNAMES_CONF_FILE"
fi

# is there a conf file?

if [[ ! -f "$CONF_FILE" ]] ; then
    echo ":error: $CONF_FILE not found, can't run"
    exit $ERROR_NO_CONF_SH
fi

# read conf file

. "$CONF_FILE" # read configuration settings

# is it the right version?

UNDERSTAND_CONF_VERSION="1"

if [[ "$CONF_VERSION" -ne "$UNDERSTAND_CONF_VERSION" ]] ; then
    echo ":error: only know how to install from v$UNDERSTAND_CONF_VERSION conf.sh"
    exit $ERROR_WRONG_VERSION_CONF_SH
fi

# make sure it's been configured

if [[ "$READY_TO_INSTALL" == "0" ]] ; then
    echo ":error: you must edit **conf.sh**, before installing"
    exit $ERROR_UNCONFIGURED
fi

# make sure all necessary files named are present and accounted for

CHECK_FOR_FILES="$BASH
$PYTHON
$TARGET"

# no quotes around CHECK_FOR_FILES, so bash treats like a list
for FILENAME in $CHECK_FOR_FILES
do
  # if the file doesn't exist, quit
  if [[ ! -e $FILENAME ]] ; then
      echo ":error: $FILENAME not found"
      exit $ERROR_NEEDED_FILE_NOT_FOUND
  fi
done

# does the target directory exist?

if [[ ! -d "$TARGET" ]] ; then
    echo ":error: $TARGET directory does not exist"
    exit $ERROR_NO_TARGET
fi

# do we write access to the target directory?

touch "$TARGET/testing-write-access"

if [[ "$?" -ne "0" ]] ; then
    echo ":error: bash process does not have write permissions to $TARGET directory"
    rm -f "$TARGET/testing-write-access"
    exit $ERROR_CANNOT_WRITE_IN_TARGET
fi

# do we have delete access to the target directory?

rm -f "$TARGET/testing-write-access"

if [[ "$?" -ne "0" ]] ; then
    echo ":error: bash process does not have delete permissions to $TARGET directory"
    exit $ERROR_CANNOT_DELETE_IN_TARGET
fi


# Doesn't return an exit code,
# since this is meant to be sourced,
# and sourcing will attach error code 0
# on successful sourcing anyways.

