# TODO
import turbogears
from turbogears import controllers

from model import Namespace, Ln, Ns, hub
from sqlobject import SQLObjectNotFound

import cherrypy

import time
import xmlrpclib



INCORRECT_PASSWORD_MSG = "Incorrect password."

TEXT_PLAIN = "text/plain; charset=utf-8"

LNXRQSs = [xmlrpclib.ServerProxy(x) for x in ["http://taoriver.net:8123/", "http://ln.taoriver.net/lnxrqs"]]


# new naming convention:
# a_  -- means "by the new naming convention"
# a_mnamespace  -- a model.Namespace
# a_mln  -- a model.LocalName
# a_mns  -- a model.NameSpace
# a_nsname  -- a name of a namespace ("lion")
# a_nsurl  -- a full namespace URL ("http://example.net/description&namespace=lion")
# a_lnname  -- a name of a local name ("slashdot")
# a_lnurl  -- a URL that is bound to a local name, or intended to be bound to a local name
# a_patternname  -- a name of a pattern
# a_patternurl  -- a URL that is bound to a pattern


def nsname_to_nsurl(a_nsname):
    """Return a url for a namespace, given the namespaces text name."""
    return (cherrypy.request.base + \
            turbogears.url("/description", namespace=a_nsname))


def dump_caches(a_nsname):
    print "dump_caches", a_nsname
    for lnxrqs in LNXRQSs:
	a_nsurl = nsname_to_nsurl(a_nsname)
	print a_nsurl
    	print lnxrqs.lnquery.dump_cache(a_nsurl)


def set_namespace_ln(a_mnamespace, a_lnname, a_lnurl):
    """Set a namespace's local name to a url.
    
    The namespace is a model.Namespace instance, the name and url are
    strings.
    
    Ensure that a local name isn't repeated.
    """
    print "set_namespace_ln", a_mnamespace, a_lnname, a_lnurl
    renamed = False
    for a_mlnOther in a_mnamespace.LNs:
        if a_mlnOther.name == a_lnname:
            a_mlnOther.url = a_lnurl
            renamed = True
    if not renamed:
        a_mlnNew = Ln(name=a_lnname, url=a_lnurl, namespace=a_mnamespace)
    dump_caches(a_mnamespace.name)
    return


def set_namespace_ns(a_mnamespace, a_nsname, a_nsurl):
    """Set a namespace's link key to a url.
    
    The namespace is a model.Namespace instance, the link_key and
    link_url are strings.
    
    Ensure that a link key isn't repeated.
    """
    renamed = False
    for a_mnsOther in a_mnamespace.NSs:
        if a_mnsOther.name == a_nsname:
            a_mnsOther.url = a_nsurl
            renamed = True
    if not renamed:
        a_mnsNew = Ns(name=a_nsname, url=a_nsurl, namespace=a_mnamespace)
    dump_caches(a_mnamespace.name)
    return


def incorrect_password_routine():
    url = turbogears.url("/")
    turbogears.flash(INCORRECT_PASSWORD_MSG)
    raise cherrypy.HTTPRedirect(url)


class Root(controllers.Root):
    @turbogears.expose(html="mylocalnames.templates.welcome")
    def index(self):
        import time
        return dict(now=time.ctime())
    
    @turbogears.expose(html="mylocalnames.templates.namespace")
    def namespace(self, namespace, password="",
                  linkkey=None, linkurl=None,
                  deltype=None,  # "LN", "NS", or "PATTERN"
                  delname=None):
        
        """Render namespace page.
        
        Aquire namespace, check password. Register links, delete links.
        """

        a_nsname = namespace
        a_nsname_linkkey = linkkey
        a_nsurl_linkurl = linkurl
        
        try:
            a_mns = Namespace.byName(a_nsname)
        except SQLObjectNotFound:
            a_mns = Namespace(name=a_nsname,
                              password=password)
            set_namespace_ln(a_mns, "this", nsname_to_nsurl(a_nsname))
        
        if a_mns.password != password:
            incorrect_password_routine()
        
        if ((a_nsname_linkkey is not None) and
            (a_nsurl_linkurl is not None)):
            set_namespace_ns(a_mns, a_nsname_linkkey, a_nsurl_linkurl)
            turbogears.flash("Link registered.")
        
        if (deltype is not None) and (delname is not None):
            for entry in {"LN": a_mns.LNs,
                          "NS": a_mns.NSs,
                          "PATTERN": a_mns.PATTERNs}.get(deltype,
                                                         a_mns.LNs):
                if entry.name == delname:
                    entry.destroySelf()
                    turbogears.flash("%s deleted" % entry.name)
        
        store_name_url = cherrypy.request.base + \
                         turbogears.url("/enter_name")
        bookmarklet_url = "javascript:o=location.href;" \
                          "location.href='%s?namespace=%s&password=%s" \
                          "&url='+escape(o)" % (store_name_url,
                                                a_nsname, password)
        
        return {"namespace": a_nsname,
                "password": password,
                "description_url": nsname_to_nsurl(a_nsname),
                "bookmarklet_url": bookmarklet_url}
    
    @turbogears.expose()
    def changepassword(self, namespace,
                       oldpassword, newpassword, repeat):
        ns = Namespace.byName(namespace)
        if ns.password != oldpassword:
            msg = INCORRECT_PASSWORD_MSG
        elif newpassword != repeat:
            msg = "The new password didn't match it's repeat."
        else:
            hub.begin()
            ns.password = newpassword
            hub.commit()
            hub.end()
            msg = "Password changed!"
        turbogears.flash(msg)
        url = turbogears.url("/namespace",
                             namespace=namespace,
                             password=ns.password)
        raise cherrypy.HTTPRedirect(url)
    
    @turbogears.expose(content_type=TEXT_PLAIN)
    def description(self, namespace):
        ns = Namespace.byName(namespace)
        result = []
        for ln_link in ns.LNs:
            result.append(u'LN "%s" "%s"' % (ln_link.name, ln_link.url))
        for ns_link in ns.NSs:
            result.append(u'NS "%s" "%s"' % (ns_link.name, ns_link.url))
        return u"\n".join(result)
    
    @turbogears.expose(html="mylocalnames.templates.enter_name")
    def enter_name(self, namespace, password, url):
        ns = Namespace.byName(namespace)
        if ns.password != password:
            incorrect_password_routine()
        return {"namespace": namespace,
                "password": password,
                "namespace_url": turbogears.url("/namespace",
                                                namespace=namespace,
                                                password=password),
                "url": url}
    
    @turbogears.expose(html="mylocalnames.templates.submit_name")
    def submit_name(self, namespace, password, name, url, confirm=None):
	a_nsname = namespace
	a_lnname = name
	a_lnurl = url
        a_mnamespace = Namespace.byName(a_nsname)
        if a_mnamespace.password != password:
            incorrect_password_routine()
        a_lnurl_lower = a_lnurl.lower()
        if ("password" in a_lnurl_lower) \
               or ("&pw=" in a_lnurl_lower) \
               or ("?pw=" in a_lnurl_lower):
            if confirm is None:
                return {"namespace": a_nsname,
                        "password": password,
                        "name": name,
                        "url": url}
        set_namespace_ln(a_mnamespace, a_lnname, a_lnurl)
        raise cherrypy.HTTPRedirect(a_lnurl)
    
    @turbogears.expose(format="json")
    def time(self):
        import time
        return {"asctime": time.asctime(),
                "time": time.time()}
    
    @turbogears.expose(content_type=TEXT_PLAIN)
    def all_namespaces(self):
        result = []
        # TODO: Correct term "name"
        for a_nsname in [a_mns.name for a_mns in Namespace.select()]:
            result.append('NS "%s" "%s"' % (a_nsname,
                                            nsname_to_nsurl(a_nsname)))
        return u"\n".join(result)

