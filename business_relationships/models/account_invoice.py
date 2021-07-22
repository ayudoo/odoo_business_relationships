# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = ["account.move"]
    _name = "account.move"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        string="Business Rel.",
        related="partner_id.business_relationship_id",
        readonly=True,
    )
