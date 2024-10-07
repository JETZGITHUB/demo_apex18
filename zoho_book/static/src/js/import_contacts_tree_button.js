odoo.define('zoho_books.contact_button', function (require) {
"use strict";
var ListController = require('web.ListController');
var ListView = require('web.ListView');
var rpc = require('web.rpc');
var viewRegistry = require('web.view_registry');
var TreeButton = ListController.extend({
   buttons_template: 'zoho_books.contact_button',
   events: _.extend({}, ListController.prototype.events, {
       'click .import': '_Import_contacts',
   }),
   _Import_contacts:function (){
   var self = this;
   self._rpc({
   model:'zoho.books',
   method:'import_contacts_zoho',
   args:[1],
   }).then(function () {
                self.do_notify('Success', 'Updated/Imported Successfully');
                location.reload();
            }).catch(function (error) {
                self.do_warn('Error', 'Importing failed: ' + error.message);
            });
        },
    });


var ResPartnerListView = ListView.extend({
   config: _.extend({}, ListView.prototype.config, {
       Controller: TreeButton,
   }),
});
viewRegistry.add('contact_button_in_tree', ResPartnerListView);
});