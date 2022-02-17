# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        string="Business Relationship",
        readonly=True,
    )

    def _query(self, with_clause="", fields={}, groupby="", from_clause=""):
        fields[
            "business_relationship_id"
        ] = ", partner.business_relationship_id as business_relationship_id"
        groupby += ", partner.business_relationship_id"
        return super()._query(with_clause, fields, groupby, from_clause)
