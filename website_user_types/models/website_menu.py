from odoo import api, fields, models


class Menu(models.Model):
    _inherit = "website.menu"

    group_ids = fields.Many2many(
        "res.groups",
        string="Visible Groups",
        help="The user needs to be in at least one of these groups to see the menu",
        domain=lambda self: [
            ("id", "in", self.env["website"].get_available_website_user_group_ids()),
        ],
    )
