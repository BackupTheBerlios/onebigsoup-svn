"""Render ln.taoriver.net website.

# TODO - debug WebsiteBuilder.list_of_names_used
#        (-->lnlink.collect_names_in_fragment)
# TODO - complete & debug WebsiteBuilder.build
# TODO - document contexts' internal variables
# TODO - final check, make sure methods and non-.variables are doc'ed
# TODO - let user tweak ExecutionContext/FileSystemContext with optparse

Read pages from pages/, and output them to website/.

The pages are first fitted into template.html, and then Local Names are
linked with localnames.txt.

PathNavigationInFilenameException  -- path found in filename
FileSystemContext  -- folder & file locations
ExecutionContext  -- all settings needed to build website
FileSystemAdapter  -- file access
WebsiteBuilder  -- build website
"""

import string
import os

import xmlrpclib

import singhtext
import localnames
import lnlink


TXT_DIRECTORY = "txt"
INPUT_DIRECTORY = "input"
OUTPUT_DIRECTORY = "output"
TEMPLATE_FILENAME = "template.html"
LOCAL_NAMESPACE_FILENAME = "localnames.txt"

OLDSTYLE_NAMESERVER_URL = "http://services.taoriver.net:9090/"

BASE_URL = "http://ln.taoriver.net/"
NAMESPACE_DESCRIPTION_URL = "http://ln.taoriver.net/localnames.txt"
NOT_FOUND_URL = "http://ln.taoriver.net/localname_not_found.txt"
CONNECTED = False  # SET THIS TO TRUE WHEN DOING REMOTE LOOKUPS


class PathNavigationInFilenameException(Exception):

    """The filename includes path navigation.

    When a filename includes the operating system separator character,
    it attempts to move beyond the boundaries of it's designated
    folder.
    """

    def __init__(self, offending_filename):
        self.offending_filename = offending_filename

    def __str__(self):
        return "Path navigation in filename: " + self.offending_filename


class FileSystemContext:

    """Store details of the filesystem context.

    The FileSystemAdapter needs to know where input files, text files,
    and output files are. It also needs to know the name of the template
    file, and the name of the localnames file. With time, these details
    may change, but- there are a lot of them. This object collects those
    details.

    There is no logic in here; write directly into instances.

    Paths must not end with a trailing slash; Use a period to
    indicate the present directory. Path navigation is forbidden in
    filenames.

    init_with_module_defaults  -- initialize with module defaults
    """

    def __init__(self):
        """Create a blank filesystem context."""
        self.path_to_text_files = None
        self.path_to_input_files = None
        self.path_to_output_files = None
        self.template_filename = None
        self.local_namespace_filename = None

    def init_with_module_defaults(self):
        """Initialize the context with module defaults.

        Module defaults are declared at the top of this modules' source.
        """
        self.path_to_text_files = TXT_DIRECTORY
        self.path_to_input_files = INPUT_DIRECTORY
        self.path_to_output_files = OUTPUT_DIRECTORY
        self.template_filename = TEMPLATE_FILENAME
        self.local_namespace_filename = LOCAL_NAMESPACE_FILENAME


class ExecutionContext:

    """Contains all settings needed to build website.

    FileSystemContext contains everything needed to access the
    filesystem, but there is more to be known. Is the user connected to
    the Internet? What is the URL of the XML-RPC server?

    This stores all settings, but it doesn't do anything with them. It
    doesn't give you an XML-RPC server object, it only stores the URL of
    the XML-RPC server object.

    There is no logic in here; write directly into instances.

    init_with_module_defaults  -- initialize with module defaults
    .filesystem_context  -- FileSystemContext to use
    .connected_to_internet  -- True/False, can make use of Internet?
    .oldstyle_xmlrpc_nameserver_url  -- XML-RPC Local Names query server
    .namespace_description_url  -- remote namespace, for names lookup
    .base_url  -- base URL for output website
    """

    def __init__(self):
        self.filesystem_context = None
        self.connected_to_internet = None
        self.oldstyle_xmlrpc_nameserver_url = None
        self.namespace_description_url = None
        self.base_url = None
        self.not_found_url = None

    def init_with_module_defaults(self):
        """Initialize the context with module defaults.

        Module defaults are declared at the top of this modules' source.
        """
        self.filesystem_context = FileSystemContext()
        self.filesystem_context.init_with_module_defaults()
        self.connected_to_internet = CONNECTED
        self.oldstyle_xmlrpc_nameserver_url = OLDSTYLE_NAMESERVER_URL
        self.namespace_description_url = NAMESPACE_DESCRIPTION_URL
        self.base_url = BASE_URL
        self.not_found_url = NOT_FOUND_URL


class FileSystemAdapter:
    
    """Mediate input/output interactions with the file system.
    
    text_file  -- read text file
    write_to_html  -- write HTML file
    template_text  -- read template text
    local_namespace_text  -- read namespace description text
    """
    
    def __init__(self, filesystem_context):
        """Initialize with a FileSystemContext."""
        self._context = filesystem_context
        self._template_text = None
        self._local_namespace_text = None
    
    def text_file(self, name):
        """Get contents of a text file.
        
        The text file is named without the .txt extension.
        """
        if os.sep in name:
            raise PathNavigationInFilenameException(name)
        filename = self._context.path_to_text_files \
                   + os.sep + name + ".txt"
        return open(filename, "r").read()

    def text_file_names(self):
        """Return list of text files.

        The text file is named without the .txt extension.
        """
        all_files = os.listdir(self._context.path_to_text_files)
        return [x[:-4] for x in all_files if x.endswith(".txt")]
    
    def write_to_html(self, name, content):
        """Write contents to an output HTML file.

        The HTML file is named without the .html extension.
        """
        if os.sep in name:
            raise PathNavigationInFilenameException(name)
        filename = self._context.path_to_output_files \
                   + os.sep + name + ".html"
        f = open(filename, "w")
        f.write(content)
        f.close()

    def template_text(self):
        """Read text of input template.

        Loads on first read.
        """
        if self._template_text is not None:
            return self._template_text
        filename = self._context.path_to_input_files \
                   + os.sep + self._context.template_filename
        self._template_text = open(filename, "r").read()
        return self._template_text
    
    def local_namespace_text(self):
        """Read text of local namespace description.
        
        Loads on first read.
        """
        if self._local_namespace_text is not None:
            return self._local_namespace_text
        filename = self._context.path_to_input_files + os.sep \
                   + self._context.local_namespace_filename
        f = open(filename, "r")
        self._local_namespace_text = f.read().decode('ascii')
        return self._local_namespace_text


class WebsiteBuilder:

    """Build the website.

    TODO: BETTER TEXT HERE.
    
    Flow process that we're moving to:

    Read each file, and build a lookup table from them.

    Add to the table whatever's found in the input localnames.txt.

    Fit each file into the template, and link the final result. Output
    the result to the output directory.

    All input/output operations are mediated by a file-system adapter.

    TODO -- function descriptions
    compile_names_dictionary  -- compile name->URL dictionary
    build  -- build website
    """

    def __init__(self, execution_context):
        """Initialize with an ExecutionContext."""
        self._context = execution_context
        self._filesystem = FileSystemAdapter(
            execution_context.filesystem_context)
        self._local_namespace = localnames.namespace_from_text(
            self._filesystem.local_namespace_text())
        if self._context.connected_to_internet:
            self._nameserver = xmlrpclib.ServerProxy(
                self._context.oldstyle_nameserver_url)
        else:
            self._nameserver = None

    def list_of_names_used(self):
        """Return set of names used in all text files."""
        names_used = set()
        for filename in self._filesystem.text_file_names():
            text = self._filesystem.text_file(filename)
            html = singhtext.text_to_html(text)
            names = set(lnlink.collect_names_in_fragment(html))
            names_used.update(names)
        return names_used

    def compile_names_dictionary(self):
        """Compile final dictionary of names to URLs.

        # Start with the input directory names.
        # Visit each text file, and strip it's provided names.
        ** Title
        ** A NAMEs
        ** (glossary entries?)
        # ...and also strip names that they want to make use of.
        # Collect missing names from nameserver, if connected to the
          Internet.

        Names that can't be found are linked to the not-found URL
        described in the execution context.
        """
        names_found = self._local_namespace["LN"].copy()
        names_used = []
        for filename in self._filesystem.text_file_names():
            text = self._filesystem.text_file(filename)
            tokens = singhtext.tokenize_all(text)
            names_provided = singhtext.tokens_to_names_list(tokens)
            text_variables = singhtext.tokens_to_variables(tokens)[0]
            if text_variables.has_key("title"):
                names_provided.append(text_variables["title"])
            for name in names_provided:
                names_found[name] = self._context.base_url + name \
                                    + ".html"
            html = singhtext.text_to_html(text)
            names_used.extend(lnlink.collect_names_in_fragment(html))
        if self._context.connected_to_internet == False:
            for name in names_used:
                if name not in names_found:
                    names_found[name] = self._context.not_found_url
        else:
            flags = ["loose", "check-neighboring-spaces"]
            namespace_url = self._context.namespace_description_url
            for name in names_used:
                if name not in names_found:
                    url = self._nameserver.lookup(name,
                                                  namespace_url,
                                                  flags)
                    names_found[name] = url
        return names_found

    def build(self):
        """Build the website.

        TODO: explain how, basically
        """
        for name in self._filesystem.text_file_names():
            text = self._filesystem.text_file(name)
            html = singhtext.text_to_html(text)
            template = self._filesystem.template_text()
            full_html = template.substitute({"BODY": html,
                                             "SECTION": "",
                                             "HEAD": ""})
            names_dict = {}


def default_builder():
    """Return a WebsiteBuilder created using module defaults.

    This is a convenience function.
    """
    execution_context = ExecutionContext()
    execution_context.init_with_module_defaults()
    return WebsiteBuilder(execution_context)


if __name__ == "__main__":
    builder = default_builder()
    builder.build()


##     # Read every file, translate it, link it, and write it out.
##     filenames = os.listdir(TXT_DIRECTORY)
##     for filename in [x for x in filenames if x.endswith(".txt")]:
##         in_filename = TXT_DIRECTORY + os.sep + filename
##         out_filename = HTML_DIRECTORY + os.sep + filename[:-4] + ".html"
##         in_file = open(in_filename, "r")
##         out_file = open(out_filename, "w")
        
##         text = singhtext.text_to_html(in_file.read())
##         text = template.substitute({"BODY": text,
##                                     "SECTION": "",
##                                     "HEAD": ""})
##         names_dict = {}
##         for name in lnlink.collect_names(text):
##             if name in names_dict:
##                 continue
##             print name,
##             if name in local_namespace["LN"]:
##                 names_dict[name] = local_namespace["LN"][name]
##             else:
##                 if not CONNECTED:
##                     names_dict[name] = "NOT-CONNECTED-CANNOT-SET-NAME"
##                 else:
##                     flags = ["loose", "check-neighboring-spaces"]
##                     url = nameserver.lookup(name,
##                                             NAMESPACE_DESCRIPTION_URL,
##                                             flags)
##                     names_dict[name] = url
##             print names_dict[name]
##         text = lnlink.link_names(text, names_dict)
        
##         out_file.write(text)

