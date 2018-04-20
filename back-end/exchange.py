

from parseUtils import parse_coinbase,parse_bitfinex
from pairs import bitfinexPairs,coinbasePairs

from tornado.websocket import websocket_connect
from tornado import httpclient

import tornado.ioloop
from tornado import escape
import json

import time


"""
This is the client class for the locally hosted websocket. This is where subscriptions are sent to the exchanges
and sent and where the snapshots and updates are parsed. Because only public channels are used for the exchange websockets,
Tornado gets a little confused because the websockets use wss, which generally require authentication. This is ignored
by making a custom http request for tornados websocket connect class that implicitly tells it to ignore SSL authentication.
The local host websocket handler is given as a parameter in this class allowing me to transfer messages from the exchange
websockets. All messages are alread parsed inside this class using imported functions from parseUtils, so the locally served
websocket only needs to determine when to start sending updates (after all snapshots are sent)

Also, if the message is important, db_utils methods are called inside this class sending the parsed info.

http://www.tornadoweb.org/en/stable/_modules/tornado/websocket.html#websocket_connect
"""
class Exchange:
    #TODO if coinbase snapshot isnt recieved, try to resubscribe
    def __init__(self,websocket,url,name):
        self.websocket = websocket
        self.name = name
        self.url = url

        self.subscribed = False
        self.connect()


    def connect(self):
        # if(self.stayClosed == True):
        #     return


        print("connecting to " + self.name)


        #need to make custom request to ignnore ssl certificaton because exchanges use wss but only public channels are used
        request = httpclient.HTTPRequest(self.url, validate_cert=False,headers={'Content-Type': 'application/json'})

        connectionFuture = websocket_connect(request,on_message_callback=self.handle_message,ping_interval=100)

        tornado.ioloop.IOLoop.current().add_future(connectionFuture,self.sendSubscription)

        # #make sure snapshot recieved in 5 seconds
        # tornado.ioloop.IOLoop.current().call_later(5,self.check_subscription)

    """
    This is only called when the websocket_connect future is finished (using IOLoop's add future functionality),
    so the argument given (connection) is assured to be a websocketconnection object.

    For coinbase, subscriptionis easy, and all cryptocurrencies can be subscribed to at once. Bitfinex is a
    little trickier, and you need to send a seperate subscription message for each pair.
    """
    def sendSubscription(self,connection):
        print("subscribing to " + self.name)

        # try:
        #     self.connection = connection.result()
        # except tornado.httpclient.HTTPError:
        #     self.stayClosed = True
        #     self.websocket.close()
        #     tornado.ioloop.IOLoop.current().stop()
        self.connection = connection.result()

        if(self.name == "bitfinex"):
            subscriptionProtocol = {#subscription message without pair key
                "event":"subscribe",
                "channel":"book",
                "freq":"F1", #updates every 2 second,
                "prec":"P1",#0 significant figures (i.e. integers)
                "len":"25" #amount of price points. defualt = 25
            }

            #loops through each pair and subscribes because you have to send seperate subscriptions for each crypto in bitfinex
            for pair in bitfinexPairs:
                subscription =  subscriptionProtocol.copy()
                subscription["pair"] = pair
                self.connection.write_message(escape.utf8(json.dumps(subscription)))#decond message to binary
        else:
            #coinbase subscription
            #it is important tso subscribe to heart beat channel even though i dont use the information
            #to make sure the connection does not drop (pretty much same as ping interval)
            subscriptionProtocol = {
                "type": "subscribe",
                "product_ids": coinbasePairs,
                "channels": ["level2","heartbeat"]
            }
            self.connection.write_message(escape.utf8(json.dumps(subscriptionProtocol)))#convert to binary and send



    """
    Parses message recieved from exchange and if the message is a snapshot or an update, writes to the locally
    served websocket with the neccessary information.
    """
    def parse_and_send(self, msg):
        message = parse_coinbase(msg) if self.name == "coinbase" else parse_bitfinex(msg) #never recieve messages on websocket with server

        if(message["type"] == "update"):
            self.websocket.handle_updates(message["data"],self.name)
        elif(message["type"] == "snapshot"):
            print("recieved snapshot from " + self.name)
            self.subscribed = True
            self.websocket.handle_snapshots(message["data"],self.name)

    # """
    # Sometimes, gdax wss doesn't always respond because their sandbox is this in the wors, so i don't get snapshot.
    # This is called after 5 seconds with ioloop future and if no snapshot was recieved, it closes the websocket and tries again.
    # """
    # def check_subscription(self):
    #     if(self.subscribed == False):
    #         print("Subscription failed. Trying again")
    #         if(self.connection):
    #             self.connection.close()
    #
    #         self.connect()


    """
    This is the callback function for whenever a new message from the client comes in. It is asnychronous.
    If the connection is lost (msg is None), then it reconnects, unless its manually closed on the server side
    from handling an error
    """
    def handle_message(self,msg):

        if msg is None:
            print("discconect from " + self.name)
            self.connect()
        elif("front-end-type" in msg):
            #comes from locally hosted web socket. message is meant for the front end. Ignore the message
            pass
        else:
            #parse the message and send it if its a snapshot or update
            self.parse_and_send(msg)
