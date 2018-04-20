from sqlalchemy import create_engine, Sequence, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker


from pairs import coinbasePairs, bitfinexPairs, pairIDs, pairFormatter
from flask import Flask




#initilize database
Base = declarative_base()

"""                                          Models                                     """

class Bid(Base):
    __tablename__ = "bid"
    id = Column(Integer,Sequence('transaction_id_seq'),primary_key=True) #primary key is the price point

    price = Column(Integer)
    amount = Column(Float) #size * amount

    pair = Column(String)
    exchange = Column(String)


    pair_id = Column(Integer,ForeignKey('pair.id'))
    exchange_id = Column(Integer,ForeignKey('exchange.id'))


class Ask(Base):
    __tablename__ = "ask"

    id = Column(Integer,Sequence('transaction_id_seq'),primary_key=True) #primary key is the price point

    price = Column(Integer)
    amount = Column(Float)

    pair = Column(String)
    exchange = Column(String)

    pair_id = Column(Integer,ForeignKey('pair.id'))
    exchange_id = Column(Integer,ForeignKey('exchange.id'))



class Pair(Base):
    __tablename__ = "pair"
    id = Column('id',Integer,primary_key=True)
    name = Column(String)


    bid = relationship("Bid")
    ask = relationship("Ask")

class Exchange(Base):
    __tablename__ = "exchange"
    id = Column('id',Integer,primary_key=True)
    name = Column(String)


    bid = relationship("Bid")
    ask = relationship("Ask")




"""                                Setup                                           """

# bind and engine to a session and create all tables
engine = create_engine('sqlite:///:memory:')#:memory: should create new db every time app is run

Session = sessionmaker(bind=engine)
db_session = Session()
Base.metadata.create_all(bind=engine)


#Add the coinbase and bitfinex to exchange table
db_session.add(Exchange(id=0,name = "coinbase"))
db_session.add(Exchange(id=1,name = "bitfinex"))


#add all pairs to the pairs table and save their id
formattedCoinbaseBairs = []
for pair in coinbasePairs:
    formattedCoinbaseBairs.append(pairFormatter(pair))
allPairs = set(bitfinexPairs + formattedCoinbaseBairs)#exchanges have different options and formats
pairID = 0
for pair in allPairs:
    db_session.add(Pair(id=pairID,name = pair))
    pairIDs[pair] = pairID
    pairID += 1


db_session.commit()
