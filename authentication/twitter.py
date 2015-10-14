__author__ = 'meramac'
import tornado.web
import tornado.httpserver
import tornado.auth
import tornado.ioloop

#The twitter handler class inherits the tornado.auth.TwitterMixin class
class TwitterHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        oAuthToken = self.get_secure_cookie('oauth_token')
        oAuthSecret = self.get_secure_cookie('oauth_secret')
        userID = self.get_secure_cookie('user_id')
        #When the user requests the root resource of the application, we first check whether the request contains an
        #oauth token query string parameter. If so, we treat the request as a callback from Twitters authorization process
        if self.get_argument('oauth_token', None):
            #We then use the auth modules method to exchange the temporary token we were given for the users access token
            #This method expects a callback
            self.get_authenticated_user(self.async_callback(self._twitter_on_auth))
            return
        #if the oauth token parameter is not found, we move on and test for the case where we have seen the user before
        elif oAuthToken and oAuthSecret:
            accessToken = {
                'key': oAuthToken,
                'secret': oAuthSecret }
            #the twitter_request method expects a resource path as its first parameter and additionally takes optional
            #keyword arguments for access_token, post_args and callback
            self.twitter_request('/users/show', access_token=accessToken,
                    user_id=userID, callback=self.async_callback(self._twitter_on_user))
            return
        #If we reach here, then the user is logging in for the first time, or has deleted her cookies, and we want to redirect
        #her to the twitter authorization page
        self.authorize_redirect()


    def _twitter_on_auth(self, user):
        if not user:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(500, 'Twitter authentication failed')
        self.set_secure_cookie('user_id', str(user['id']))
        self.set_secure_cookie('oauth_token', user['access_token']['key'])
        self.set_secure_cookie('oauth_secret', user['access_token']['secret'])
        #Now the user gets redirected to /user/show
        self.redirect('/')


    def _twitter_on_user(self, user):
        if not user:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(500, "Couldn't retrieve user information")
        self.render('home.html', user=user)


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_all_cookies()
        self.render('logout.html')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            #Twittermixin has to be used on the handler that you registered in twitter for the callback url
        (r'/', TwitterHandler), (r'/logout', LogoutHandler)
        ]
        settings = {
        'twitter_consumer_key': 'dfdfdf',
        'twitter_consumer_secret': 'dfdf',
        'cookie_secret': 'NTliOTY5NzJkYTVlMTU0OTAwMTdlNjgzMTA5M2U3OGQ5NDIxZmU3Mg==', 'template_path': 'templates',
        }
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()