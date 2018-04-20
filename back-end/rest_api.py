from flask_restless import APIManager
from flask import Flask
from db_declerative import db_session, Bid, Ask, Pair, Exchange


#create flask flaskApp
flaskApp = Flask(__name__)
manager = APIManager(flaskApp, session=db_session)



#allow access from anywhere, so front-end can make calls
def add_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response

flaskApp.after_request(add_cors_header)



#create end points (max results per page = -1 means show all data on one page. for the scope of this project)
#it doesn't make a difference
manager.create_api(Bid,max_results_per_page=-1,exclude_columns=['exchange_id','pair_id'])
manager.create_api(Ask,max_results_per_page=-1,exclude_columns=['exchange_id','pair_id'])
manager.create_api(Pair,max_results_per_page=-1)
manager.create_api(Exchange,max_results_per_page=-1,include_columns=['asks','bids'])
