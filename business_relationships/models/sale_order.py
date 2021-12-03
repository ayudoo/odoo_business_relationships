# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        related="partner_id.business_relationship_id",
        readonly=True,
    )

    @api.onchange('partner_shipping_id', 'partner_id', 'company_id')
    def onchange_partner_shipping_id(self):
        res = super().onchange_partner_shipping_id()
        shipping_pricelist_id = self.partner_shipping_id.property_product_pricelist
        if shipping_pricelist_id and shipping_pricelist_id != self.pricelist_id:
            if self.business_relationship_id.sale_order_pricelist == "shipping":
                self.pricelist_id = shipping_pricelist_id.id

        return res

    @api.model
    def create(self, vals):
        self._set_enforced_values(vals)

        record = super().create(vals)
        if record.partner_id != record.partner_shipping_id:
            record.onchange_partner_shipping_id()

        return record

    def _set_enforced_values(self, values):
        partner_id = values.get('partner_id', False)
        if not partner_id:
            return

        partner = self.env['res.partner'].browse(partner_id)
        if partner.business_relationship_id.enforce_salesperson_website:
            if partner.business_relationship_id.salesperson_id:
                values['user_id'] = partner.business_relationship_id.salesperson_id.id

    def write(self, values):
        r = super().write(values)
        if "partner_shipping_id" in values or "partner_id" in values:
            self.onchange_partner_shipping_id()
        return r
