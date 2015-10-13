from uuid import uuid4
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpserver


__author__ = 'meramac'

class ShoppingCart:
    inventory = 10
    carts = {}
    callbacks = []
    def register(self,callback):
        self.callbacks.append(callback)

    def moveItemToCart(self,session):
        if session in self.carts:
            return
        self.carts[session] = True
        self.notifyCallbacks()

    def removeItemFromCart(self,session):
        if session not in self.carts:
            return
        del(self.carts[session])
        self.notifyCallbacks()

    def getInventoryCount(self):
        return self.inventory - len(self.carts)
    def notifyCallbacks(self):
        self.callbacks[:] = [c for c in self.callbacks if self.callbackHelper(c)]
    def callbackHelper(self, callback):
        callback(self.getInventoryCount())
        return False


class DetailHandler(tornado.web.RequestHandler):
    def get(self):
        session = uuid4()
        count = self.application.shoppingCart.getInventoryCount()
        self.render("index.html", session=session, count=count)

class CartHandler(tornado.web.RequestHandler):
    def post(self):
        action = self.get_argument('action')
        session = self.get_argument('session')
        if not session:
            self.set_status(400)
            return
        if action == 'add':
            self.application.shoppingCart.moveItemToCart(session)
        elif action == 'remove':
            self.application.shoppingCart.removeItemFromCart(session)
        else:
            self.set_status(400)

class StatusHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.application.shoppingCart.register(self.on_message)
    def on_message(self, count):
        self.write('{"inventoryCount":"%d"}' % count)
        self.finish()

class Application(tornado.web.Application):
    def __init__(self):
        self.shoppingCart = ShoppingCart()
        handlers = [
                    (r'/', DetailHandler), (r'/cart', CartHandler), (r'/cart/status', StatusHandler)
                    ]
        settings = {
            'template_path': 'templates', 'static_path': 'static'
        }
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()