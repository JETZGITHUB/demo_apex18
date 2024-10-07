odoo.define('zoho_book.refresh_page', function(require){
 'use strict'
 console.log("vanthuttennu sollu, 25 varushathukku munnadi kabali epdi ponano, apdiye thirumbi vanthuttannu sollu")
// openerp.zoho_book = function (instance) {
//    instance.web.ActionManager = instance.web.ActionManager.extend({
//        ir_actions_act_close_wizard_and_reload_view: function (action, options) {
//            if (!this.dialog) {
//                options.on_close();
//            }
//            this.dialog_stop();
//            this.inner_widget.views[this.inner_widget.active_view].controller.reload();
//            return $.when();
//        },
//    });
  var BusService = require('bus.BusService');
    var core = require('web.core');
    var _t = core._t;

    BusService.include({
        init: function () {
            this._super.apply(this, arguments);
            this._notification = false;
        },
        poll: function () {
            this._super.apply(this, arguments);
            if (this._notification) {
                this.do_notify(_t('Notification'), this._notification, true);
                this._notification = false;
            }
        },
        sendone: function (message) {
            this._super.apply(this, arguments);
            if (message[0] === 'notification') {
                this._notification = message[1];
            }
        },
    });
//}

});