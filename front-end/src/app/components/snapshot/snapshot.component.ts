import { Component, OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { SnapshotService } from '../../services/snapshot.service';
import {DataSource} from '@angular/cdk/collections';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';


@Component({
    selector: 'snapshot-component',
    templateUrl: './snapshot.component.html',
    styleUrls: ['./snapshot.component.css']
})

export class SnapshotComponent implements OnInit {

    rForm: FormGroup;

    bidDataSource = new BidDataSource(this.snapshotService);
    askDataSource = new AskDataSource(this.snapshotService);

    displayedColumns = ['pair','price','amount','exchange'];

    pairs = ["BTCUSD","ETHUSD"] //TODO make this dynamic so i dont have to hard code it in
    filter : String;
    constructor(private fb: FormBuilder,private snapshotService : SnapshotService,private router: Router) {

        this.rForm = fb.group({
            'filter' : [''],
        });



    }

    ngOnInit() {
        //TODO switch to the new rForm api and using async validators and regex
        //subscribe to forms and update filter if important change
        this.rForm.get("filter").valueChanges.subscribe((val) => {
            var lowercase = val.toLowerCase();
            var uppercase = val.toUpperCase();
            var strAsInt = parseInt(val);//only integer price points
            //send information to the snapshot service to filter the datatable
            if(lowercase == "coinbase" || lowercase == "bitfinex"){
                this.snapshotService.filter({"exchange":lowercase});
            }else if(this.pairs.indexOf(uppercase) != -1 ){
                this.snapshotService.filter({"pair":uppercase});
            }else if(isNaN(strAsInt) == false){
                this.snapshotService.filter({"minPrice":strAsInt});
            }else{
                this.snapshotService.filter({})//no filters
            }
        });
    }

    public goToRealtime(){
        this.router.navigateByUrl("/realtime-order-book")
    }

}



export class BidDataSource extends DataSource<any> {

    constructor(private orderService: SnapshotService) {
        super();
    }

    //all the websocket updates happen in the order service. the data source just has to observe it for changes
    connect() {
        return this.orderService.bidsChange.asObservable();
    }

    disconnect() {}
}



export class AskDataSource extends DataSource<any> {

    constructor(private orderService: SnapshotService) {
        super();
    }

    //all the websocket updates happen in the order service. the data source just has to observe it for changes
    connect() {
        return this.orderService.asksChange.asObservable();
    }

    disconnect() {}
}
