#
# install.sh
#
# (c) 2004 Lion Kimbro - released into public domain
#
#
# How to run:
#
#    $ ./install.sh
#
#
# This:
#   * is a tool managing my.localnames installation
#   * relies on "conf.sh"
#   * performs basic sanity checks
#   * installs "index.cgi", ".htaccess"
#   * installs Python scripts
#
# This DOES NOT:
#   * create & permission the TARGET directory
#   * alter httpd.conf
#
#   ...you must do those things yourself.
#
#
# APACHE:
#
#   This does NOT configure Apache (httpd.conf) for you!
#
#   We supply a .htaccess file, but you'll need to
#   enable "AllowOverride All" yourself, for the target
#   installation directory..!
#
#   Your httpd.conf entry MAY look something like:
#
#   Alias /mylocalnames/ "/var/www/my.localnames/"
#   <Directory "/var/www/my.localnames/">
#       AllowOverride All
#   </Directory>
#
#
# SEE ALSO:
#   * uninstall.sh
#


########################################
# SMOKE TESTS
########################################

. ./sh_conftests.sh

if [[ "$?" -ne "0" ]] ; then
    exit $?
fi


########################################
# PERFORM INSTALLATION
########################################

function check_file()
{
    if [[ ! -f "$1" ]] ; then
	echo ":error: couldn't create $1"
	exit 255
    fi
}


# build boot cgi

CGI_FILE="index.cgi"
FULL_CGI_FILE="$TARGET/$CGI_FILE"

echo '#!'"$BASH" > "$FULL_CGI_FILE"
echo "$PYTHON code_handlerqst.py" >> "$FULL_CGI_FILE"

chown "$CHOWN_TO" "$FULL_CGI_FILE"
chmod 775 "$FULL_CGI_FILE"

check_file "$FULL_CGI_FILE"


# build htaccess
#
#   THIS NEEDS SOME HELP;
#   Specificly, on my testing computer,
#   it seems that accessing the directory
#   itself doesn't work- you have to
#   specifly name index.cgi within the
#   directory.
#
#   I had hoped that "DirectoryIndex" would
#   be enough, but, for some reason,
#   it doesn't seem to be.
#
#   Please help fix this, should you know how.
#
cp "htaccess" "$TARGET/.htaccess"
check_file "$TARGET/.htaccess"


# build conf.py

FULL_CONF_PY_FILE="$TARGET/conf.py"

echo "XMLRPC_LN_SERVER='$XMLRPC_LN_SERVER'" > "$FULL_CONF_PY_FILE"
echo "URL_DOMAIN_NAME='$URL_DOMAIN_NAME'" >> "$FULL_CONF_PY_FILE"
echo "URL_DIRECTORY_BASE='$URL_DIRECTORY_BASE'" >> "$FULL_CONF_PY_FILE"

check_file "$FULL_CONF_PY_FILE"


# copy files

cp *.html "$TARGET"
cp *.css "$TARGET"
cp *.py "$TARGET"
cp *.png "$TARGET"


# create a data directory

if [ ! -d "$TARGET/data" ] ; then
    mkdir "$TARGET/data"
    chown "$CHOWN_TO" "$TARGET/data"
    chmod 775 "$TARGET/data"
fi

# if not exists data summary file, create it

if [ ! -f "$TARGET/data.p" ] ; then
    cp data.p "$TARGET"
    chown "$CHOWN_TO" "$TARGET/data.p"
    chmod 664 "$TARGET/data.p"
fi


# done!

exit $SUCCESS

