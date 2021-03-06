__author__ = 'meramac'
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import pymongo
#options is used to read options from the command line. If you use --help then it will give the options
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/(\w+)", WordHandler)]
        conn =  pymongo.MongoClient("localhost", 27017)
        #Once we have added the db attribute to the application object we can access it in any request handler object
        self.db = conn["example"]
        tornado.web.Application.__init__(self, handlers, debug=True)

class WordHandler(tornado.web.RequestHandler):
    def get(self, word):
        coll = self.application.db.words
        word_doc = coll.find_one({"word": word})
        if word_doc:
            del word_doc["_id"]
            self.write(word_doc)
        else:
            self.set_status(404)

    def post(self, word):
        definition = self.get_argument("definition")
        coll = self.application.db.words
        word_doc = coll.find_one({"word": word})
        if word_doc:
            word_doc['definition'] = definition
            coll.save(word_doc)
        else:
            word_doc = {'word': word, 'definition': definition}
            coll.insert(word_doc)
        del word_doc["_id"]
        self.write(word_doc)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        greeting = self.get_argument("greeting","hello")
        #this will write to the http response
        self.write(greeting + ", friendly user !")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()