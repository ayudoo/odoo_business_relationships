from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        string="Business Relationship",
        readonly=True,
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["business_relationship_id"] = "partner.business_relationship_id"
        return res

    def _group_by_sale(self):
        return super()._group_by_sale() + ", partner.business_relationship_id"
