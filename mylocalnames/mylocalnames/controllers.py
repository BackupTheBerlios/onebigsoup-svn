import turbogears
from turbogears import controllers

from model import Namespace, Ln, Ns, hub
from sqlobject import SQLObjectNotFound

import cherrypy


INCORRECT_PASSWORD_MSG = "Incorrect password."

TEXT_PLAIN = "text/plain; charset=utf-8"


def set_namespace_ln(namespace, name, url):
    """Set a namespace's local name to a url.
    
    The namespace is a model.Namespace instance, the name and url are
    strings.
    
    Ensure that a local name isn't repeated.
    """
    for local_name in namespace.LNs:
        if local_name.name == name:
            local_name.name = name
            return
    local_name = Ln(name=name, url=url, namespace=namespace)
    return


def set_namespace_ns(namespace, link_key, link_url):
    """Set a namespace's link key to a url.
    
    The namespace is a model.Namespace instance, the link_key and
    link_url are strings.
    
    Ensure that a link key isn't repeated.
    """
    for ns_link in namespace.NSs:
        if ns_link.name == link_key:
            ns_link.url = link_url
            return
    ns_link = Ns(name=link_key, url=link_url, namespace=namespace)
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
    def namespace(self, namespace, password,
                  linkkey=None, linkurl=None,
                  deltype=None, delname=None):
        
        """Render namespace page.
        
        Aquire namespace, check password. Register links, delete links.
        """
        
        try:
            ns = Namespace.byName(namespace)
        except SQLObjectNotFound:
            ns = Namespace(name=namespace,
                           password=password)
        
        if ns.password != password:
            incorrect_password_routine()
        description_url = turbogears.url("/description",
                                         namespace=namespace)
        
        if (linkkey is not None) and (linkurl is not None):
            set_namespace_ns(ns, linkkey, linkurl)
            turbogears.flash("Link registered.")
        
        if (deltype is not None) and (delname is not None):
            for entry in {"LN": ns.LNs,
                          "NS": ns.NSs}.get(deltype, ns.LNs):
                if entry.name == delname:
                    entry.destroySelf()
                    turbogears.flash("%s deleted" % entry.name)
        
        store_name_url = cherrypy.request.base + \
                         turbogears.url("/enter_name")
        bookmarklet_url = "javascript:o=location.href;" \
                          "location.href='%s?namespace=%s&password=%s" \
                          "&url='+escape(o)" % (store_name_url,
                                                namespace, password)
        
        return {"namespace": namespace,
                "password": password,
                "description_url": description_url,
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
    
    @turbogears.expose()
    def description(self, namespace):
        ns = Namespace.byName(namespace)
        result = []
        cherrypy.response.headerMap['Content-Type'] = TEXT_PLAIN
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
    
    @turbogears.expose()
    def submit_name(self, namespace, password, name, url):
        ns = Namespace.byName(namespace)
        if ns.password != password:
            incorrect_password_routine()
        set_namespace_ln(ns, name, url)
        raise cherrypy.HTTPRedirect(url)

