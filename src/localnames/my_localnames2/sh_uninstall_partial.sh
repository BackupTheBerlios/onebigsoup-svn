#
# sh_uninstall_partial.sh
#
# (c) 2004 Lion Kimbro - released into public domain
#
#
# How to run:
#
#    $ ./sh_uninstall_partial.sh
#
#
# This:
#   * removes everything, EXCEPT user data
#
#
# APACHE:
#
#   This script deletes .htaccess, but does NOT
#   touch httpd.conf!
#
#
# SEE ALSO:
#
#   * install.sh
#


########################################
# SMOKE TESTS
########################################

. ./sh_conftests.sh

if [[ "$?" -ne "0" ]] ; then
    exit $?
fi


########################################
# UNINSTALL
########################################

rm "$TARGET"/*.html
rm "$TARGET"/*.css
rm "$TARGET"/*.py
rm "$TARGET"/*.png

rm "$TARGET"/.htaccess
rm "$TARGET"/conf.py
rm "$TARGET"/index.cgi


if [[ "$?" -ne "0" ]] ; then
    echo ":error: could not delete all files in $TARGET"
    exit $ERROR_CANNOT_DELETE_IN_TARGET
fi

if [[ `ls $TARGET | grep -v data | wc -l` -ne "0" ]] ; then
    echo ":error: still files in $TARGET"
    exit $ERROR_CANNOT_DELETE_IN_TARGET
fi


exit $SUCCESS

