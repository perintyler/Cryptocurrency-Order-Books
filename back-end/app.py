
import tornado.ioloop
import tornado.web
from tornado.wsgi import WSGIContainer


from websocket_handler import WebsocketHandler
import db_declerative
import db_utils

from rest_api import flaskApp

def main():
    wsApp = tornado.web.Application([(r"/", WebsocketHandler)])
    http_server = tornado.httpserver.HTTPServer(wsApp)
    http_server.listen(8080)

    api_http_server = tornado.httpserver.HTTPServer(WSGIContainer(flaskApp))
    api_http_server.listen(5000)
    #create rest api server (flask)
    # apiApp = tornado.web.Application([])
    # manager = flask_restless.APIManager(apiApp, session=db_session)

    #api_http_server.listen(5000)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
