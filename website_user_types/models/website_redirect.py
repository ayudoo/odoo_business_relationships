from odoo import fields, models


class WebsiteRedirect(models.Model):
    _inherit = "website.rewrite"

    group_ids = fields.Many2many(
        "res.groups",
        string="Visible Groups",
        help=(
            "The user needs to be in at least one of these groups for the redirect to"
            + " have effect"
        ),
    )

    redirect_type = fields.Selection(
        selection_add=[("403", "403 Forbidden")],
    )
