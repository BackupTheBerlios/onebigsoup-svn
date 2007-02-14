import xmlrpclib

__author__ = "TheCrypto - thecrypto at thecrypto dot org"
__version__ = "1.0 (2005-01-08)"
__description__ = "Implements XMLRPCFilterPipes"

filterurls = {
	'markdown': 'http://services.taoriver.net:9001/markdown/',
	'localnames': 'http://services.taoriver.net:9090/',
	'smartypants': 'http://services.taoriver.net:9001/smartypants/'
}
def verify_installation(request):
	config = request.getConfiguration()
	if not (config.has_key('cacheDriver') and config.has_key('cacheConfig')):
		print "this plugin requires caching to be enabled because it"
		print "relys on external servers running. please enable one"
		print "of the caches before using this plugin"
		return 0
	if not config.has_key('filterurls'):
		print "missing optional config property 'filterurls' which allows "
		print "you to specify additional XMLRPCFilteringPipes. refer to "
		print "xmlrpcfilter plugin documentation for more details."
	return 1
def cb_postformat(args):
	config = args['request'].getConfiguration()
	if not (config.has_key('cacheDriver') and config.has_key('cacheConfig')):
		return
	if config.has_key('filterurls'):
		filterurls.update(config['filterurls'])
	if not args['entry_data'].has_key('xmlrpcfilters'):
		return
	filterlist = args['entry_data']['xmlrpcfilters'].split()
	filters = {}
	currentfilter = ""
	for filtername in filterlist:
		if "=" in filtername:
			if not currentfilter == "":
				keyvaluepair = filtername.split("=", 1)
				filters[currentfilter]['args'][keyvaluepair[0]] = keyvaluepair[1]
		elif filtername in filterurls:
			currentfilter = filtername
			filters[filtername] = {'args': {}}
	for filter in filters:
		url = filterurls[filter]
		function_name = "wiki.filterData"
		data = xmlrpclib.Binary(args['entry_data']['body'])
		encoding = "text/plain; charset=utf-8"
		proxy = xmlrpclib.ServerProxy(url)
		response = getattr(proxy, function_name)(data, encoding, filters[filter]['args'])
		if type(response) == type("string"):
			args['entry_data']['body'] = "Problem running filter ", filter, " Recieved error" , str(response)	
			break
		else:
			args['entry_data']['body'] = str(response['data'])

