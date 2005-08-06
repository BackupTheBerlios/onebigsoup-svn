import xmlrpclib
lnstore = xmlrpclib.ServerProxy("http://localnames.sosdg.org:9001/jroes")
lnstore.get_server_info("password")
# {'INTERFACE': 'v1 Local Names Store Interface', 'IMPLEMENTATION': 'JROES-LNS-D3-V1', 'SUPPORTS_PRIVATE_NAMESPACES': 0, 'URL_NAME_PATTERN': '', 'SERVER_NAMESPACE_URL': ''}
lnstore.change_password("testing", "test")
# """[-4, "User Doesn't Exist"]"""
lnstore.create_user("jroes", "jroes@sosdg.org", "testing")
# """[-3, 'Internal Server Error']"""
lnstore.create_user("jroes@sosdg.org", "testing")
# [-3, 'Internal Server Error']
lnstore = xmlrpclib.ServerProxy("http://localnames.sosdg.org:9001")
lnstore.create_user("jroes", "jroes@sosdg.org", "testing")
# [0, 'OK']
lnstore = xmlrpclib.ServerProxy("http://localnames.sosdg.org:9001/jroes")
lnstore.change_password("testing", "test")
# [0, 'OK']
lnstore.change_password("testing", "test")
# [-4, 'Incorrect Password']
lnstore.change_password("test", "testing")
# [0, 'OK']
lnstore.create_namespace("testing", "my_great_namespace")
# [0, 'OK']
lnstore.create_namespace("testing", "delete_me")
# [0, 'OK']
lnstore.delete_namespace("testing", "delete_me")
# [0, 'OK']
lnstore.delete_namespace("testing", "delete_me")
# [-100, "Namespace Doesn't Exist"]
lnstore.get_namespaces("testing")
# ['my_great_namespace']
lnstore.create_namespace("testing", "test_namespace")
# [0, 'OK']
lnstore.get_namespaces("testing")
# ['test_namespace', 'my_great_namespace']
lnstore.delete_namespace("testing", "test_namespace")
# [0, 'OK']
lnstore.get_namespaces("testing")
# ['my_great_namespace']
lnstore.get_namespace_url("testing", "my_great_namespace")
# 'http://localnames.sosdg.org/jroes-my_great_namespace'
lnstore.create_namespace("testing", "test_namespace")
# [0, 'OK']
lnstore.get_namespace_url("testing", "test_namespace")
# 'http://localnames.sosdg.org/jroes-test_namespace'
lnstore.create_namespace("testing", "testing")
# [0, 'OK']
lnstore.get_namespaces("testing")
# ['testing', 'my_great_namespace']
lnstore.set("testing", "testing", "LN", "Robotic Nation", "http://marshallbrain.com/robotic-nation.htm")
# [0, 'OK']
lnstore.get_namespaces("testing")
# ['testing', 'my_great_namespace']
lnstore.get_namespace_url("testing", "testing")
# 'http://localnames.sosdg.org/jroes-testing'
lnstore.get_namespace_url("testing", "testin'")
# [-100, "Namespace Doesn't Exist"]
lnstore.unset("testing", "testing", "LN", "Robotic Nation", "http://marshallbrain.com/robotic-nation .htm")
# [0, 'OK']

