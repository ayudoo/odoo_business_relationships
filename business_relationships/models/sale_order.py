from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        related="partner_id.business_relationship_id",
        readonly=True,
    )

    @api.onchange("partner_id")
    def _br_onchange_partner_id(self):
        br = self.partner_id.business_relationship_id
        if br:
            self.update(br.get_sale_order_default_values(include_false=True))

    @api.onchange("partner_shipping_id", "partner_id", "company_id")
    def onchange_partner_shipping_id(self):
        shipping_pricelist_id = self.partner_shipping_id.property_product_pricelist
        if shipping_pricelist_id and shipping_pricelist_id != self.pricelist_id:
            if self.business_relationship_id.update_pricelist_by == "shipping":
                if self.pricelist_id.id != shipping_pricelist_id.id:
                    self.pricelist_id = shipping_pricelist_id.id

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            self._set_business_relationship_values(values)

        orders = super().create(values_list)

        for order in orders:
            update_by = order.partner_id.business_relationship_id.update_pricelist_by
            if (
                update_by == "shipping"
                and order.partner_id != order.partner_shipping_id
            ):
                order.onchange_partner_shipping_id()

        return orders

    def _set_business_relationship_values(self, values):
        partner_id = values.get("partner_id", False)
        if not partner_id:
            return

        partner = self.env["res.partner"].browse(partner_id)
        br = partner.business_relationship_id

        for name, value in br.get_sale_order_default_values().items():
            if not values.get(name, None):
                values[name] = value

        if self.env.context.get("website_id"):
            if br.enforce_salesperson_website and br.salesperson_id:
                values["user_id"] = br.salesperson_id.id
            if br.enforce_team_website and br.team_id:
                values["team_id"] = br.team_id.id
