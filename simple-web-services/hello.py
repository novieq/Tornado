__author__ = 'meramac'
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

#options is used to read options from the command line. If you use --help then it will give the options
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        greeting = self.get_argument("greeting","hello")
        #this will write to the http response
        self.write(greeting + ", friendly user !")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/",IndexHandler)])
    #This is a single threaded server
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

