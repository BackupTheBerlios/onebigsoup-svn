import sha

def getfoaf(serverurl, userinfo):
       returnstring = "Content-Type: application/rdf+xml\n\n"
       returnstring += '''
       <rdf:RDF
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
       xmlns:foaf="http://xmlns.com/foaf/0.1/"
       xmlns:admin="http://webns.net/mvcb/">
       <foaf:PersonalProfileDocument rdf:about="">
       <foaf:maker rdf:nodeID="me"/>
       <foaf:primaryTopic rdf:nodeID="me"/>
       <admin:generatorAgent rdf:resource="%s"/>
       <admin:errorReportsTo rdf:resource="mailto:jroes@sosdg.org"/>
       </foaf:PersonalProfileDocument>
       <foaf:Person rdf:nodeID="me">''' % (serverurl,)
       if userinfo.has_key("firstname") and userinfo.has_key("lastname"):
              returnstring += '<foaf:name>%s %s</foaf:name><foaf:givenname>%s</foaf:givenname><foaf:family_name>%s</foaf:family_name>' % (userinfo['firstname'], userinfo['lastname'], userinfo['firstname'], userinfo['lastname'])
       if userinfo.has_key("email"):
              returnstring += '<foaf:mbox_sha1sum>%s</foaf:mbox_sha1sum>' % sha.new(userinfo['email']).hexdigest()
       if userinfo.has_key("homepage"):
              returnstring += '<foaf:homepage rdf:resource="%s" />' % userinfo['homepage']
       if userinfo.has_key("picture"):
              returnstring += '<foaf:depiction rdf:resource="%s" />' % userinfo['picture']
       if userinfo.has_key("plog_uri"):
              returnstring += '<foaf:plog_url rdf:resource="%s" />' % userinfo['plog_uri']
       returnstring += '</foaf:Person></rdf:RDF>'
       return returnstring 
