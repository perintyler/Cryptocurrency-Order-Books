import tornado.websocket
import tornado.ioloop

from exchange import Exchange
from pairs import bitfinexPairs
from db_utils import update_db, populate_db
from parseUtils import aggregate
from pairs import bitfinexPairs
import operator


"""
This is the locally hosted web socket handler, which sends an initial snapshot of a compiled order book
to the front-end, and then will send subsequent updates. It connects to clients (exchanges), combines their
snapshots, and echos their updates. Incoming data from clients recieved is  parsed inside the exchange class.

http://www.tornadoweb.org/en/stable/websocket.html =
"""
class WebsocketHandler(tornado.websocket.WebSocketHandler):


    #connect to bitfinex and coinbase
    def open(self):
        print("opening local websocket")

        self.snapshots = {"bitfinex":[]}
        self.subscribed = False #becomes true when snapshots are recieved from both exchanges


        self.coinbase = Exchange(self,"wss://ws-feed-public.sandbox.gdax.com","coinbase")
        self.bitfinex = Exchange(self,"wss://api.bitfinex.com/ws","bitfinex")



    def check_origin(self, origin):
        #TODO check if this is neccessary
        #get domain ending using: urllib.parse.urlparse(origin).netloc.endswith(".mydomain.com")
        #and make sure the domain ending is from bitfinex and gdax
        return True


    """
    Update recieved from exchange. Update the db and write a message to the front-end
    """
    def handle_updates(self,msg,exchangeName):
        update_db(msg,exchangeName)

        #incoming protocol: {bidOrAsk,pair,price,amout,exchange}
        #outgoing protocol: {front-end-type,bidOrAsk,update:{[pair,price,amout,exchange]}}

        for update in msg:
            bidOrAsk = update["bidOrAsk"]
            updateCopy = dict(update)#because db could be working on same dict (value not ref)
            del updateCopy["bidOrAsk"]
            self.write_message({"front-end-type":"update","bidOrAsk":bidOrAsk,"update":updateCopy})#specify message is for the front-end so clients ignore



            # try:
            #     self.write_message({"front-end-type":"update","bidOrAsk":bidOrAsk,"update":updateCopy})#specify message is for the front-end so clients ignore
            # except tornado.websocket.WebSocketClosedError:
            #     print("Websocket Closed Error")
            #     self.coinbase.stayClosed = True
            #     self.bitfinex.stayClosed = True
            #     self.coinbase.connection.close()
            #     self.bitfinex.connection.close()
                #tornado.ioloop.IOLoop.current().stop()




    """
    Snapshot recieved from exchange. Waits for all snapshots to be recieved, then sends the combined
    snapshots to the database and front-end (sorted). Snapshots are only sent to the front-end once so
    snapshots received from a client that disconnects and reconnects will be ignored.
    """
    def handle_snapshots(self,msg,exchangeName):
        #if snapshots are already sent, ignore this message. It is a snapshot from a reconnect
        if(self.subscribed == True):
            return

        print("Local websocket recieved snapshot from " + exchangeName)
        if(exchangeName == "coinbase"):
            self.snapshots["coinbase"] = aggregate(msg)
        else:#bitfinex
            bids = []
            asks = []
            for order in msg:
                bidOrAsk = order["bidOrAsk"]
                orderCopy = order.copy()
                del orderCopy["bidOrAsk"]
                if(bidOrAsk == "bid"):
                    bids.append(orderCopy)
                else:
                    asks.append(orderCopy)
            self.snapshots["bitfinex"].append({"bids":bids,"asks":asks})

        #check to see if all snapshots are recieved, and if so, combined/sort and send
        if("coinbase" in self.snapshots and len(self.snapshots["bitfinex"])==len(bitfinexPairs)):
            combinedBids = []
            combinedAsks = []

            #combine all snapshots from bitfinex with the snapshot from coinbase
            for snapshot in self.snapshots["bitfinex"]:
                combinedBids += snapshot["bids"]
                combinedAsks += snapshot["asks"]
            combinedBids += self.snapshots["coinbase"]["bids"]
            combinedAsks += self.snapshots["coinbase"]["asks"]


            #send the combined snapshots to the db, creating the order book
            populate_db(combinedBids,combinedAsks)

            #sort for front end table display (highest prices on top)
            combinedBids.sort(key=operator.itemgetter('price'),reverse=True)
            combinedAsks.sort(key=operator.itemgetter('price'),reverse=True)

            #send order book to front end
            self.write_message({"front-end-type":"snapshot","bids":combinedBids,"asks":combinedAsks});

            # try:
            #     self.write_message({"front-end-type":"snapshot","bids":combinedBids,"asks":combinedAsks});
            # except tornado.websocket.WebSocketClosedError:
            #     self.coinbase.stayClosed = True
            #     self.bitfinex.stayClosed = True
            #     self.coinbase.connection.close()
            #     self.bitfinex.connection.close()
            #     #tornado.ioloop.IOLoop.current().stop()
            # else:
            #     #subscribe so any subsequent snapshots will be ignored
            #     self.subscribed = True
