import { Injectable } from '@angular/core';
import { HttpClient,HttpParams }   from '@angular/common/http';
import { Observable }   from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import { Order } from '../models/order.model';
import {BehaviorSubject} from 'rxjs/BehaviorSubject';

@Injectable()
export class SnapshotService {
    private apiUrl= 'http://localhost:5000/api/';

    bidsChange: BehaviorSubject<Order[]> = new BehaviorSubject<Order[]>([]);
    asksChange: BehaviorSubject<Order[]> = new BehaviorSubject<Order[]>([]);
    originalBids = []
    originalAsks = []

    isFiltered = false;

    pairIDs = {"BTCUSD":0,"ETHUSD":1};//TODO make this an api request so it doesn;t have to be hard coded in

    constructor(private http: HttpClient) {
        //clunky, but need to populate original bids and asks to 'unfilter' so cannot just use this.updateTable(apiUrl)
        var bidsRequest = this.http.get<Order[]>(this.apiUrl + 'bid')
        bidsRequest.subscribe(val => {
            this.originalBids = val["objects"];
            this.bidsChange.next(val["objects"]);
        });


        var asksRequest = this.http.get<Order[]>(this.apiUrl + 'ask')
        asksRequest.subscribe(val => {
            this.originalAsks = val["objects"];
            this.asksChange.next(val["objects"])

        });
    }

    update_table(url){
        var bidsRequest = this.http.get<Order[]>(url + "bid")
        bidsRequest.subscribe(val => {
            console.log(val['objects'])
            this.bidsChange.next(val["objects"]);
        });


        var asksRequest = this.http.get<Order[]>(url + "ask")
        asksRequest.subscribe(val => {
            this.asksChange.next(val["objects"])
        });
    }

    filter(options){
        if("exchange" in options){
            //reset to original value
            //make call to exchange table with correct id which contains a relation with bid and ask

            var exchangeID = ( (options["exchange"] == "coinbase") ? 0 : 1 )
            this.update_table(this.apiUrl + 'exchange/' + exchangeID + '/');
        }
        else if("minPrice" in options) {
            //filter out all rows with minimum value less than

            //find bids in original snapshot with price greater than min price
            var filteredBids = []
            for(var i = 0;i<this.originalBids.length;i++){
                if(parseInt(this.originalBids[i].price) > options["minPrice"]){
                    const copy = { ...this.originalBids[i] } //make copy of dict

                    filteredBids.push(copy);
                }
            }

            //find bids in original snapshot with price less than min price
            var filteredAsks = []
            for(var i = 0;i<this.originalAsks.length;i++){
                if(parseInt(this.originalAsks[i].price) > options["minPrice"]){
                    const copy = { ...this.originalAsks[i] }

                    filteredAsks.push(copy)
                }
            }

            this.bidsChange.next(filteredBids);
            this.asksChange.next(filteredAsks);
        }else if("pair" in options){
            //make call to table table with correct id which contains a relation with bid and ask

            var pairID = this.pairIDs[options["pair"]];
            this.update_table(this.apiUrl + 'pair/' + pairID + '/');
        }else{

            //no filters. make sure table is in original state
            this.bidsChange.next(this.originalBids)
            this.asksChange.next(this.originalAsks)

        }


    }

    getBids() {
        return this.bidsChange;
    }

    getAsks() {
        return this.asksChange;
    }
}
