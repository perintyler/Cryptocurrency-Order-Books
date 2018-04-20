import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/of';
import {DataSource} from '@angular/cdk/collections';
import { OrderService } from '../../services/order.service';
import {BehaviorSubject} from 'rxjs/BehaviorSubject';
import { Order } from '../../models/order.model';
import { Router } from '@angular/router';




@Component({
    selector: 'real-time',
    templateUrl: './realtime.component.html',
    styleUrls: ['./realtime.component.css']
})

export class RealtimeComponent implements OnInit {

    bidDataSource = new BidDataSource(this.orderService);
    askDataSource = new AskDataSource(this.orderService);

    displayedColumns = ['pair','price','amount','exchange'];

    constructor(private orderService: OrderService,private router: Router) {

    }

    ngOnInit() {
        //set Title

    }

    public goToSnapshot(){
        this.orderService.closeWebsocket();
        this.router.navigateByUrl("/order-book-snapshot")
    }

}

export class BidDataSource extends DataSource<any> {

    constructor(private orderService: OrderService) {
        super();
        orderService.openWebsocket()
    }

    //all the websocket updates happen in the order service. the data source just has to observe it for changes
    connect() {
        return this.orderService.bidsChange.asObservable()
    }

    disconnect() {}
}



export class AskDataSource extends DataSource<any> {

    constructor(private orderService: OrderService) {
        super();
    }

    //all the websocket updates happen in the order service. the data source just has to observe it for changes
    connect() {
        return this.orderService.asksChange.asObservable()
    }

    disconnect() {}
}
