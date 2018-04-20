import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs/BehaviorSubject';
import {Order} from '../models/order.model';

import { Observable } from 'rxjs';
import 'rxjs/add/observable/of';

@Injectable()
export class OrderService {

    bids = [];
    asks = [];
    bidsChange: BehaviorSubject<Order[]> = new BehaviorSubject<Order[]>([]);
    asksChange: BehaviorSubject<Order[]> = new BehaviorSubject<Order[]>([]);
    websocket : WebSocket;

    constructor() {
    }

    closeWebsocket(){
        //this.websocket.close();
    }

    openWebsocket(){
        //create connection to websocket set up on local host
        this.websocket = new WebSocket('ws://localhost:8080');

        /**             Set Up Websocket events                 **/

        this.websocket.onmessage = event => {

            var msg = JSON.parse(event.data);

            if(msg['front-end-type']=="snapshot"){
                this.bids = msg["bids"];
                this.asks = msg["asks"];


                this.bidsChange.next(this.bids);
                this.asksChange.next(this.asks);
            }else{
                //update
                if(msg["bidOrAsk"]=="bid"){
                    var update = msg["update"];
                    var index = this.bids.findIndex(key => key.price == update["price"]);

                    if(index==-1){
                        //price not in table. add to table
                        this.bids.push(update);
                    }else{
                        //price point in table. update table
                        this.bids[index] = update;
                    }
                    this.bidsChange.next(this.bids);
                }else{
                    //ask
                    var update = msg["update"];
                    var index = this.asks.findIndex(key => key.price == update["price"]);
                    this.asks[index] = update;
                    this.asksChange.next(this.asks);
                }


            }

        }
    }
}
