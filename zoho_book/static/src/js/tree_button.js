odoo.define('zoho_books.tree_button', function (require) {
"use strict";

var ListController = require('web.ListController');
var ListView = require('web.ListView');
var rpc = require('web.rpc');
var viewRegistry = require('web.view_registry');
var TreeButton = ListController.extend({
   buttons_template: 'zoho_books.buttons',
   events: _.extend({}, ListController.prototype.events, {
       'click .import': '_Import',
   }),

//   _Import:function (){
//   rpc.query({
//   model:'zoho.books',
//   method:'import_items_zoho',
//   args:[1],
//   });
//   return this.do_notify('Success', 'Importing');
//   },
//
//});
    _Import: function () {
            var self = this;
            self._rpc({
                model: 'zoho.books',
                method: 'import_items_zoho',
                args: [1],
            }).then(function () {
                self.do_notify('Success', 'Importing completed');
                location.reload();
            })
            .catch(function () {
                self.do_warn('Error', 'Importing failed: ');
            });
        },
//        _Import: function () {
//            var self = this;
//            rpc.query({
//                model: 'zoho.books',
//                method: 'import_items_zoho',
//                args: [1],
//            }).then(function () {
//                self.do_notify('Success', 'Importing completed');
//            });
//        },
    });
//    _Import: function () {
//            var self = this;
//            rpc.query({
//                model: 'zoho.books',
//                method: 'import_items_zoho',
//                args: [1],
//            }).then(function (result) {
//                if (result === 'No Items To Update.') {
//                    self.do_notify('Info', 'No Items To Update.');
//                }
//                if (result === 'Action Success') {
//                    self.do_notify('Success', 'Importing completed');
//                }
//            }).catch(function (error) {
//                self.do_warn('Error', 'Importing failed: ' + error.message);
//            });
//        },
//    });

var ProductTemplateListView = ListView.extend({
   config: _.extend({}, ListView.prototype.config, {
       Controller: TreeButton,
   }),
});




viewRegistry.add('button_in_tree', ProductTemplateListView);
});
