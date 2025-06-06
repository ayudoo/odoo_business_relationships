from odoo import api, fields, models


class Menu(models.Model):
    _inherit = "website.menu"

    group_ids = fields.Many2many(
        "res.groups",
        string="Visible Groups",
        help="The user needs to be in at least one of these groups to see the menu",
        domain=lambda self: [
            ("id", "in", self.env["res.groups"]._wut_get_selectable_groups().ids),
        ],
    )

    def _compute_visible(self):
        super()._compute_visible()
        if self.user_has_groups("base.group_user,!website.group_website_designer"):
            for record in self:
                if record.group_ids and not record.group_ids & self.env.user.groups_id:
                    record.is_visible = False
