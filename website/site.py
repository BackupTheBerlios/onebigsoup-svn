"""Render ln.taoriver.net website.

Read pages from pages/, and output them to website/.

The pages are first fitted into template.html, and then Local Names are
linked with localnames.txt.
"""

import string
import os

import xmlrpclib

import singhtext
import localnames
import lnlink


TXT_DIRECTORY = "txt"
HTML_DIRECTORY = "html"
TEMPLATE_FILENAME = "template.html"
OLDSTYLE_NAMESERVER_URL = "http://services.taoriver.net:9090/"
LOCAL_NAMESPACE_FILENAME = "localnames.txt"
NAMESPACE_DESCRIPTION_URL = "http://ln.taoriver.net/localnames.txt"
CONNECTED = False  # SET THIS TO TRUE WHEN DOING REMOTE LOOKUPS


class FileSystemAdapter:

    """Mediate all input/output interactions with the file system.

    TODO -- name functions
    """

    def __init__(self, path_to_text_files,
                 location_of_localnames,
                 path_to_output_files):
        """Initialize with locations.

        Paths must not end with a trailing slash; Use a period to
        indicate the present directory.

        Location must be a path + a filename. You may ignore the path if
        the file is in the working directory.
        """
        self.path_to_text_files = path_to_text_files
        self.location_of_localnames = location_of_localnames
        self.path_to_output_files = path_to_output_files


"""Flow process that we're moving to:

Read each file, and build a lookup table from them.

Add to the table whatever's found in the input localnames.txt.

Fit each file into the template, and link the final result. Output the
result to the output directory.

All input/output operations are mediated by a file-system adapter.
"""


for (input_filename, output_filename) in filesystem.productions():
    f = open(input_filename, "r")
    singhtext.read_names(


if __name__ == "__main__":
    # Read out the page template from a text file.
    template_text = open(TEMPLATE_FILENAME, "r").read()
    template = string.Template(template_text)

    # Read out Local Names from a text file.
    local_namespace_text = open(
        LOCAL_NAMESPACE_FILENAME, "r").read().decode("ascii")
    local_namespace = localnames.namespace_from_text(
        local_namespace_text)

    # Prepare the names server.
    nameserver = xmlrpclib.ServerProxy(OLDSTYLE_NAMESERVER_URL)

    # Read every file, translate it, link it, and write it out.
    filenames = os.listdir(TXT_DIRECTORY)
    for filename in [x for x in filenames if x.endswith(".txt")]:
        in_filename = TXT_DIRECTORY + os.sep + filename
        out_filename = HTML_DIRECTORY + os.sep + filename[:-4] + ".html"
        in_file = open(in_filename, "r")
        out_file = open(out_filename, "w")
        
        text = singhtext.text_to_html(in_file.read())
        text = template.substitute({"BODY": text,
                                    "SECTION": "",
                                    "HEAD": ""})
        names_dict = {}
        for name in lnlink.collect_names(text):
            if name in names_dict:
                continue
            print name,
            if name in local_namespace["LN"]:
                names_dict[name] = local_namespace["LN"][name]
            else:
                if not CONNECTED:
                    names_dict[name] = "NOT-CONNECTED-CANNOT-SET-NAME"
                else:
                    flags = ["loose", "check-neighboring-spaces"]
                    url = nameserver.lookup(name,
                                            NAMESPACE_DESCRIPTION_URL,
                                            flags)
                    names_dict[name] = url
            print names_dict[name]
        text = lnlink.link_names(text, names_dict)
        
        out_file.write(text)

