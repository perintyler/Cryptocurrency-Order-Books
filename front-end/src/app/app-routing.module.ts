import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {RealtimeComponent} from './components/realtime/realtime.component'
import {SnapshotComponent} from './components/snapshot/snapshot.component'




const routes: Routes = [
  { path:'', redirectTo:'/realtime-order-book', pathMatch: 'full'},
  { path:'realtime-order-book', component: RealtimeComponent },
  { path:'order-book-snapshot', component: SnapshotComponent }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes,{ enableTracing: true }) ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
