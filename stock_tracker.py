import redis,os,os.path
import cherrypy
import logging, sys, logging.config

logger = logging.getLogger()
LOG_CONF = {
    'version': 1,

    'formatters': {
        'void': {
            'format': ''
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'cherrypy_console': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'void',
            'stream': 'ext://sys.stdout'
        },
        'cherrypy_access': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'void',
            'filename': os.getcwd() + '/' + 'access.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'cherrypy_error': {
            'level':'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'void',
            'filename': os.getcwd() + '/' + 'errors.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO'
        },
        'cherrypy.access': {
            'handlers': ['cherrypy_access'],
            'level': 'INFO',
            'propagate': False
        },
        'cherrypy.error': {
            'handlers': ['cherrypy_console', 'cherrypy_error'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
conf = {
	'/': {
		'tools.sessions.on': True,
		'tools.staticdir.root': os.path.abspath(os.getcwd())
	},
	'/search': {
		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		'tools.response_headers.on': True,
		'tools.response_headers.headers': [('Content-Type', 'text/plain')],
	},
	'/static': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './public'
	}
}

class StockTracker(object):
	
	@cherrypy.expose
	def index(self):
		""" This function returns the top 10 stocks stored in Redis DB"""
		cherrypy.log("START: index:StockTracker")
		data = []
		cherrypy.log("Creating a Redis instance")
		r = redis.StrictRedis()
		result = ""
		cherrypy.log("Fetching top 10 stocks stored in Redis DB")
		for i in range(2,12):
			stock_details = r.hgetall("stock:"+str(i))
			data.append(stock_details)
		for temp in data:
			result += """<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>""".format(temp["code"],temp["name"],temp["open"],temp["high"],temp["low"],temp["close"]) 

		cherrypy.log("Serving the template")
		file = open('index.html')
		index_html = file.read()
		file.close()
		index_html = index_html.format(result)
		cherrypy.log("END: index:StockTracker")		
		return index_html
		
		
@cherrypy.expose
class StockTrackerWebService(object):

	@cherrypy.tools.accept(media='text/plain')
	def GET(self, name=""):
		""" This function returns stock details of a particular stock by name"""
		cherrypy.log("START: search:StockTrackerWebService method=GET name="+name)

		cherrypy.log("Creating Redis instance")
		r = redis.StrictRedis()

		search = ""
		keys = []
		
		###################################################################################
		#  Retrieving stock details for a particular name                                 #
		###################################################################################
		if str(name).isspace():
			return ""
		elif len(name) == 0:
			data = []
			r = redis.StrictRedis()
			for i in range(2,12):
				stock_details = r.hgetall("stock:"+str(i))
				data.append(stock_details)
			for temp in data:
				search += """<table><tbody><tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tbody></table>""".format(temp["code"],temp["name"],temp["open"],temp["high"],temp["low"],temp["close"]) 
			return search
		keys = r.keys('stock:name:*'+str(name).replace(" ","").lower()+'*')
		cherrypy.log("Retreiving stock details for name="+name)
		if len(keys) == 0:
			cherrypy.log("No stock details found for name="+name)
			return ""
		for key in keys:
			stock_id = r.get(key)
			stock_details = r.hgetall("stock:"+stock_id)
			search += """<table cellpadding="0" cellspacing="0" border="0"><tbody><tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tbody></table>""".format(stock_details["code"],stock_details["name"],stock_details["open"],stock_details["high"],stock_details["low"],stock_details["close"]) 
		cherrypy.log("END: search:StockTrackerWebService method=GET name="+name)
		return search


cherrypy.config.update({'log.screen': False,'log.access_file': '','log.error_file': ''})
cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)
logging.config.dictConfig(LOG_CONF)
if __name__ == '__main__':
	webapp = StockTracker()
	webapp.search = StockTrackerWebService()
	cherrypy.quickstart(webapp, '/', conf)