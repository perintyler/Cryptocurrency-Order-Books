import json

"""                                     Bitfinex                                                                    """

#bitfinex is super annoying and only gives channel ids instead of pair names for updates. Channel ids are assigned in the
#subscription response and change every time you connect, i have to map each pairname to its channel id to parse updates
bitfinexChannelIDs = {}



# update protocol: [chanelid,price,count,amount]
# snapshot protocol: [chanelid,[ [price,count,amount] ] ]
def parse_bitfinex(msg):
    message = json.loads(msg);

    #Subscription response. map the channel ids to its pair name to use to parse updates and snapshots
    if("event" in message and message["event"]=="subscribed"):
        bitfinexChannelIDs[message["chanId"]] = message["pair"]
        return {"type":"subscription"}

    #info event or heart beat event which isn't neeeded. This message is ignored
    elif("event" in message or message[1]=="hb"):
        return {"type":"info"}

    #update message
    elif(len(message)== 4):

        pairName = bitfinexChannelIDs[ message[0] ]
        price = float(message[1])
        count = float(message[3])  #negative means ask. for some reason, bitfinex calls amount what others call count
        amount = price*count

        #i return it as an array because coinbase sends multiple updates at a time
        #so it just makes it easier in the webscoket handler, so i can just loop through
        #updates everytime, even if the array size is only 1 for bitfinex
        order = [pairName,price,amount,"bitfinex"]
        return format_orders("update",[order])

    #snapshot message
    else:

        orders = []

        pairName = bitfinexChannelIDs[ message[0] ]
        book_orders = message[1]
        for order in book_orders:
            price = float(order[0])
            count = float(order[2])
            amount = price*count
            orders.append([pairName,price,amount,"bitfinex"])

        return format_orders("snapshot",orders)


"""                                     Coinbase                                                                    """

# update protocol: [type, product_id, changes: [ [buy or sell, updated price, updated size] ] ]
# snapshot protocol: [type, product_id, bids:[ [price,size] ], asks:[ [price,size] ] ]

def parse_coinbase(msg):
    message = json.loads(msg)

    #snapshot message
    if(message["type"] == "snapshot"):

        orders = []

        pairName = message["product_id"]
        #loop through both the bids and the asks array and send each order booking to server

        for bid in message["bids"]:
            price = float(bid[0])
            count = float(bid[1])
            amount = price*count

            orders.append([pairName,int(price),amount,"coinbase"])
            #add_transaction(pairName,price,count,amount,"coinbase")//TODO

        for ask in message["asks"]:
            price = int(float(ask[0]))
            count = float(ask[1])
            amount = -1*price*count#negative

            orders.append([pairName,price,amount,"coinbase"])


        return format_orders("snapshot",orders)

    #COINBASE UPDATE
    #NOTES:
    #   - The price and size are not deltas to last snapshot, they are updated values
    #   - The updates are given as a listself.

    elif(message["type"] == "l2update"):
        #NOTE: I think updates are being sent in different web socket frames in one write or something
        #because im not getting lists of updates. look into this

        changes = message["changes"]
        pairName = message["product_id"]

        changes = message["changes"]

        updates = []

        for change in changes:
            price = float(change[1])
            size = float(change[2])#count
            amountModifier = -1 if changes[0] == "sell" else 1 #if sell,multiple amount by -1
            amount = amountModifier * price * size
            updates.append([pairName,price,amount,"coinbase"])


        return format_orders("update",updates)

    #this will be a subscription, heartbeat message, or error message which is ignored
    #error messages can be ignored because disconnects are handled.
    else:
        return {"type":"sub-or-hb"}



#coinbase level2 channel is suppose to send a agregated top 50 orders snapshot, but it isn't (?maybe because custom http request?)
#so I have to aggregate coinbase snapshot myself. I just aggregate to 0 significant figures (integers)
def aggregate(orders):
    pricePoints = {}
    for order in orders:
        bidOrAsk = order["bidOrAsk"]

        roundedPrice = int(order["price"])
        if(roundedPrice in pricePoints):
            pricePoints[roundedPrice] += order["amount"] if order["bidOrAsk"] == "bid" else -1*order["amount"]
        else:
            pricePoints[roundedPrice] = order["amount"] if order["bidOrAsk"] == "bid" else -1*order["amount"]

    bids = []
    asks = []
    for price, amount in pricePoints.items():
        roundedAmount = round(abs(amount),2)
        if(roundedAmount>0):
            bids.append({"price":price,"amount":roundedAmount,"exchange":order["exchange"],"pair":order["pair"]})
        elif(roundedAmount<0):
            asks.append({"price":price,"amount":roundedAmount,"exchange":order["exchange"],"pair":order["pair"]})

    return {"bids":bids,"asks":asks}


"""                                     Formatting                                                                    """

def format_orders(messageType,orders):
    formattedOrders = []

    for order in orders:
        pair = order[0]
        price = order[1]
        amount = order[2]
        exchange = order[3]

        formattedOrders.append(format_helper(pair,price,amount,exchange))

    return {
        "type": messageType,
        "data": formattedOrders
    }

def format_helper(pairName,price,amount,exchange):

    if(exchange == "coinbase"):
        #map coinbase pair name to bitfinex format
        pair = pairName[:3] + pairName[4:] #removes the dash that coinbase pairs use
    else:
        pair = pairName

    bidOrAsk = "bid" if float(amount) > 0 else "ask" #negative amount -> ask

    return {
        "bidOrAsk":bidOrAsk,
        "pair":pair,
        "price":price,
        "amount":round(abs(amount),2),#no need for negative amounts because it is implied in the type (bid or ask)
        "exchange":exchange
    }
