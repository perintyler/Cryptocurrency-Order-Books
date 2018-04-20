//angular modules
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

//componenents
import { AppComponent } from './app.component';
import {RealtimeComponent} from './components/realtime/realtime.component'
import { SnapshotComponent } from './components/snapshot/snapshot.component';

//services
import {OrderService} from './services/order.service'
import { SnapshotService } from './services/snapshot.service';

//routing
import { AppRoutingModule } from './app-routing.module';

//material modules
import { MatTableModule} from '@angular/material/';
import { MatButtonModule} from '@angular/material/button';
import { MatToolbarModule} from '@angular/material/toolbar';

//for rest api
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';



@NgModule({
  imports: [
    BrowserModule,
    MatTableModule,
    MatToolbarModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule
  ],
  declarations: [
    AppComponent,
    RealtimeComponent,
    SnapshotComponent
  ],
  providers: [OrderService,SnapshotService],
  bootstrap: [AppComponent]
})
export class AppModule { }
