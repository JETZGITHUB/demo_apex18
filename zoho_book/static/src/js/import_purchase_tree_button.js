odoo.define('zoho_books.purchase_button', function (require) {
"use strict";

var ListController = require('web.ListController');
var ListView = require('web.ListView');
var rpc = require('web.rpc');
var viewRegistry = require('web.view_registry');
var NotificationService = require('web.NotificationService');


var TreeButton = ListController.extend({
   buttons_template: 'zoho_books.purchase_button',
   events: _.extend({}, ListController.prototype.events, {
       'click .import': '_Import_purchase',
   }),
   _Import_purchase:function (){
   var self = this;
   self._rpc({
   model:'zoho.books',
   method:'import_purchase_zoho',
   args:[1],
}).then(function (result) {
            console.log(result);
            if (result.length > 0) {
                 console.log("ulllaa vanthutan");
                  self.do_warn('Info', result.length + "Records" + 'Not Imported');
                 }
            if (result.count > 0){
                  self.do_notify('Success', result.count + "Record "+'Imported/Updated Successfully');
                 }location.reload();
            });
        },
//        _Import_purchase:function (){
//           var self = this;
//           self._rpc({
//           model:'zoho.books',
//           method:'import_purchase_zoho',
//           args:[1],
//        }).then(function () {
//                      location.reload();
////                    console.log(result);
////                    if (result.length > 0) {
////                         console.log("ulllaa vanthutan");
////                          self.do_warn('Info', result.length + "Records" + 'Not Imported');
////                         }
////                    if (result.count > 0){
////                          self.do_notify('Success', result.count + "Record "+'Imported/Updated Successfully');
////                         }location.reload();
//                    });
//                },
    });
var PurchaseOrderListView = ListView.extend({
   config: _.extend({}, ListView.prototype.config, {
       Controller: TreeButton,
   }),
});
viewRegistry.add('purchase_button_in_tree', PurchaseOrderListView);
});
