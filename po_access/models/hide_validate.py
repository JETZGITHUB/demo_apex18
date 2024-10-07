from odoo import api, models, fields, _
# from odoo14.odoo.osv import osv


class ResUsers(models.Model):
    _inherit = 'res.users'

    role = fields.Many2many('po.access', string='Role')


class PoAccess(models.Model):
    _name = 'po.access'

    name = fields.Char(string='Role')
    receive_access = fields.Boolean('PO Recevie Access')
    validate_access = fields.Boolean('PO Validate Access')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    validate_invisible = fields.Boolean(compute='compute_get')

    def compute_get(self):
        print("default")
        uid = self._context.get('uid')
        user = self.env['res.users'].browse(uid)
        print(user.role.validate_access)
        if user.role.receive_access == True and user.role.validate_access == True:
            self.validate_invisible = True
            print(self.user_id)
        else:
            self.validate_invisible = False
            print(self.user_id)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def compute_invisible(self):
        uid = self._context.get('uid')
        user = self.env['res.users'].browse(uid)
        print(user.role.validate_access)

        if user.role.receive_access == True:
            self.receive_invisible = True
        else:
            self.receive_invisible = False

    receive_invisible = fields.Boolean(compute="compute_invisible", string="Receive invisible")



