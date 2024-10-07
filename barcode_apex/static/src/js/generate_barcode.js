odoo.define('barcode_apex.kanban_button', function(require) {
   "use strict";
   var KanbanController = require('web.KanbanController');
   var KanbanView = require('web.KanbanView');
   var viewRegistry = require('web.view_registry');
   var KanbanButton = KanbanController.include({
       buttons_template: 'barcode_apex.kanban_button',
       events: _.extend({}, KanbanController.prototype.events, {
           'click .generate_barcode_kanban': '_GenerateBarcode',
       }),
       _GenerateBarcode: function (){
   var self = this;
   self._rpc({
   model:'product.template',
   method:'generate_barcodes',
   args:[1],
   }).then(function () {
                self.do_notify('Success', 'Updated/Imported Successfully');
                location.reload();
            }).catch(function (error) {
                self.do_warn('Error', 'Importing failed: ' + error.message);
            });
        },
   });
   var ProductTemplateKanbanView = KanbanView.extend({
       config: _.extend({}, KanbanView.prototype.config, {
           Controller: KanbanButton
       }),
   });
   viewRegistry.add('button_in_kanban', ProductTemplateKanbanView);
});