
from pairs import coinbasePairs, bitfinexPairs, getPairID

from db_declerative import db_session, Base, Bid, Ask, Pair, Exchange






def create_order(bidOrAsk,pricePoint,amount,pair,exchange):
    pairID = getPairID(pair)
    exchangeID = 0 if exchange == "coinbase" else 1
    if(bidOrAsk == "bid"):
        return Bid(price=pricePoint,amount=amount,pair=pair,exchange=exchange,pair_id=pairID,exchange_id=exchangeID)
    else:
        return Ask(price=pricePoint,amount=amount,pair=pair,exchange=exchange,pair_id=pairID,exchange_id=exchangeID)



"""
This gets called when all snapshots are recieved. Creates the initial order book
"""
def populate_db(bids,asks):
    for bid in bids:
        order = create_order("bid",bid["price"],bid["amount"],bid["pair"],bid["exchange"])
        db_session.add(order)

    for ask in asks:
        order = create_order("ask",ask["price"],ask["amount"],ask["pair"],ask["exchange"])
        db_session.add(order)

    db_session.commit()




#pair,price,bidOrAsk,count,amount,exchange
def update_db(updates,exchange):
    for update in updates:
        bidOrAsk = update["bidOrAsk"]
        pricePoint = int(update["price"])
        amount = update["amount"]
        pairID = getPairID(update["pair"])
        exchangeID = 0 if exchange == "coinbase" else 1

        query = db_session.query(Bid) if(bidOrAsk == "bid") else db_session.query(Ask)
        order = query.filter_by(price = pricePoint, pair_id = pairID, exchange_id = exchangeID).first()

        #First check to see if the bid or ask exists at that price point. if it doesn't create a new bid or ask
        if not order:
            db_session.add(create_order(bidOrAsk,pricePoint,amount,update["pair"],update["exchange"]))

        elif(order.amount == 0):
            #order exists but amount is 0, which means it should be deleted from the order book
            db_session.delete(order)
        else:
            #update order book with new values
            order.amount = amount

    #commit changes
    db_session.commit()
