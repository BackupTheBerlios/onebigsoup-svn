"""Render ln.taoriver.net website.

* TODO - let user tweak ExecutionContext/FileSystemContext with optparse
* TODO - get code to where I can use it for my personal website, if it's
         not already at that point

Read pages from txt/, and output them to website/.

The pages are first fitted into template.html, and then Local Names are
linked with localnames.txt.

The specifics of filenames and paths can be customized.

PathNavigationInFilenameException  -- path found in filename
FileSystemContext  -- folder & file locations
ExecutionContext  -- all settings needed to build website
FileSystemAdapter  -- file access
WebsiteBuilder  -- build website
basic_builder  -- build default WebsiteBuilder
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

LOCAL_FILE_ENCODING = 'cp1252'  # Windows ANSI Codepage 1252

BASE_URL = "http://ln.taoriver.net/"
NAMESPACE_DESCRIPTION_URL = "http://ln.taoriver.net/localnames.txt"
NOT_FOUND_URL = "http://ln.taoriver.net/localname_not_found.html"

LOCALNAMES_SEPARATOR = ":"

OLDSTYLE_NAMESERVER_URL = "http://services.taoriver.net:9090/"

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
    .path_to_text_files  -- where to read content text files
    .path_to_input_files  -- where to read miscellaneous files
    .path_to_output_files  -- where to write output files
    .template_filename  -- filename, HTML template file
    .local_namespace_filename  -- filename, base local names description
    .file_encoding  -- encoding of text files on local filesystem
    """

    def __init__(self):
        """Create a blank filesystem context."""
        self.path_to_text_files = None
        self.path_to_input_files = None
        self.path_to_output_files = None
        self.template_filename = None
        self.local_namespace_filename = None
        self.file_encoding = None

    def init_with_module_defaults(self):
        """Initialize the context with module defaults.

        Module defaults are declared at the top of this modules' source.
        """
        self.path_to_text_files = TXT_DIRECTORY
        self.path_to_input_files = INPUT_DIRECTORY
        self.path_to_output_files = OUTPUT_DIRECTORY
        self.template_filename = TEMPLATE_FILENAME
        self.local_namespace_filename = LOCAL_NAMESPACE_FILENAME
        self.file_encoding = LOCAL_FILE_ENCODING


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
    .localnames_separator  -- local names separator character
    .oldstyle_xmlrpc_nameserver_url  -- XML-RPC Local Names query server
    .namespace_description_url  -- remote namespace, for names lookup
    .base_url  -- base URL for output website, with trailing slash
    .not_found_url  -- URL for lookups that can't be resolved
    """

    def __init__(self):
        self.filesystem_context = None
        self.connected_to_internet = None
        self.localnames_separator = None
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
        self.localnames_separator = LOCALNAMES_SEPARATOR
        self.oldstyle_xmlrpc_nameserver_url = OLDSTYLE_NAMESERVER_URL
        self.namespace_description_url = NAMESPACE_DESCRIPTION_URL
        self.base_url = BASE_URL
        self.not_found_url = NOT_FOUND_URL


class FileSystemAdapter:
    
    """Mediate input/output interactions with the file system.
    
    The page's filenames are in three categories:
    * "basename"  - ex: "index"
    * "textname"  - ex: "index.txt"
    * "htmlname"  - ex: "index.html"
    
    text_file  -- read text file
    text_file_basenames  -- list text files
    write_to_html  -- write HTML file
    template_text  -- read template text
    local_namespace_text  -- read namespace description text
    """
    
    def __init__(self, filesystem_context):
        """Initialize with a FileSystemContext."""
        self._context = filesystem_context
        self._template_text = None
        self._local_namespace_text = None

    def text_file(self, basename):
        """Get contents of a text file.
        
        The text file is named without the .txt extension.
        """
        if os.sep in basename:
            raise PathNavigationInFilenameException(basename)
        filename = self._context.path_to_text_files \
                   + os.sep + basename + ".txt"
        encoding = self._context.file_encoding
        return open(filename, "r").read().decode(encoding)

    def text_file_basenames(self):
        """Return list of text files.

        The text file is named without the .txt extension.
        """
        all_files = os.listdir(self._context.path_to_text_files)
        basenames = []
        for x in all_files:
            if x.endswith(".txt"):
                basenames.append(unicode(x[:-4]))
        return basenames
    
    def write_to_html(self, basename, content):
        """Write contents to an output HTML file.

        The HTML file is named without the .html extension.
        """
        if os.sep in basename:
            raise PathNavigationInFilenameException(basename)
        filename = self._context.path_to_output_files \
                   + os.sep + basename + ".html"
        f = open(filename, "w")
        f.write(content.encode(self._context.file_encoding))
        f.close()

    def template_text(self):
        """Read text of input template.
        
        Loads on first read.
        """
        if self._template_text is not None:
            return self._template_text
        filename = self._context.path_to_input_files \
                   + os.sep + self._context.template_filename
        text = open(filename, "r").read()
        self._template_text = string.Template(text)
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

    The class makes use of the ExecutionContext to learn about
    customizations to the process, including the embedded
    FileSystemContext. Most of the functionality is about how to extract
    names provided and used from the various files. The "build" function
    describes, specificly, how the website is built.

    url_from_basename  -- build a URL from a basename
    fit_html_inside_template  -- render text within the template
    names_used_by_template  -- get names used by the template
    names_used_by_text_file  -- get names used in one text file
    names_used_by_all_text_files  -- get names used in all text files
    names_provided_by_text_file  -- get names from one text file
    names_provided_by_all_text_files  -- get names from all text files
    names_provided_by_localnames_file  -- get names from localnames.txt
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
    
    def url_from_basename(self, basename):
        """Return URL representing HTML rendered from a text file."""
        return self._context.base_url + basename + ".html"

    def fit_html_inside_template(self, html):
        """Return result of placing given html into the template."""
        template = self._filesystem.template_text()
        return template.substitute({"BODY": html,
                                    "SECTION": "",
                                    "HEAD": ""})
    
    def names_used_by_template(self):
        """Return set of names used in the template file."""
        template_without_text = self.fit_html_inside_template("")
        return lnlink.collect_names(template_without_text).unresolved

    def names_used_by_text_file(self, basename):
        """Return set of names used by one text file."""
        names_used = set()
        text = self._filesystem.text_file(basename)
        html = singhtext.text_to_html(text)
        return lnlink.collect_names_in_fragment(html).unresolved
        
    def names_used_by_all_text_files(self):
        """Return set of names used in all text files."""
        names_used = set()
        for basename in self._filesystem.text_file_basenames():
            names_used.update(self.names_used_by_text_file(basename))
        return names_used

    def names_provided_by_text_file(self, basename):
        """Return dictionary of names provided by one text file."""
        names_dict = {}
        file_url = self.url_from_basename(basename)
        text = self._filesystem.text_file(basename)
        tokens = singhtext.tokenize_all(text)
        variables = singhtext.tokens_to_variables(tokens)[0]
        if variables.has_key("title"):
            title = variables["title"]
        else:
            title = basename
        names_dict[title] = file_url
        for name in singhtext.tokens_to_names_list(tokens):
            names_dict[name] = file_url + "#" + name
        return names_dict
    
    def names_provided_by_all_text_files(self):
        """Return dictionary of names provided by text files."""
        names_dict = {}
        for basename in self._filesystem.text_file_basenames():
            provided = self.names_provided_by_text_file(basename)
            names_dict.update(provided)
        return names_dict

    def names_provided_by_localnames_file(self):
        """Return dictionary of Local Names from localnames.txt."""
        return self._local_namespace["LN"].copy()
    
    def build(self):
        """Build the website.
        
        The process works like so:
        # Compile all names, both wanted & provided,
        ** from the template
        ** from the local names description,
        ** from text files,
        # XML-RPC for names still wanted,
        # then render and record pages.

        All input/output operations are mediated by the execution
        context's FileSystemAdapter.
        """
        collection = lnlink.CollectedNames()
        collection.update(self.names_used_by_template())
        collection.update(self.names_used_by_all_text_files())
        collection.bind(self.names_provided_by_localnames_file())
        collection.bind(self.names_provided_by_all_text_files())
        if self._context.connected_to_internet:
            collection.bind_with_LNQS(
            self._context.namespace_description_url,
            self._context.oldstyle_xmlrpc_nameserver_url,
            self._context.localnames_separator)
        collection.bind_unresolved_to_url(self._context.not_found_url)
        for name in self._filesystem.text_file_basenames():
            text = self._filesystem.text_file(name)
            html = singhtext.text_to_html(text)
            full_html = self.fit_html_inside_template(html)
            linked_html = lnlink.link_names(full_html, collection)
            self._filesystem.write_to_html(name, linked_html)


def basic_builder():
    """Return a WebsiteBuilder created using module defaults.

    This is a convenience function.
    """
    execution_context = ExecutionContext()
    execution_context.init_with_module_defaults()
    return WebsiteBuilder(execution_context)


if __name__ == "__main__":
    builder = basic_builder()
    builder.build()

