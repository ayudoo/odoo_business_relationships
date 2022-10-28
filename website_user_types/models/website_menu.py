from odoo import fields, models


class Menu(models.Model):
    _inherit = "website.menu"

    group_ids = fields.Many2many(
        "res.groups",
        string="Visible Groups",
        help=(
            "The user needs to be in at least one of these groups for the page to"
            + " be visible"
        ),
    )
