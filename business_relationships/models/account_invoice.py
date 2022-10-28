from odoo import fields, models


class AccountMove(models.Model):
    _inherit = ["account.move"]
    _name = "account.move"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        string="Business Relationship",
        related="partner_id.business_relationship_id",
        readonly=True,
    )
