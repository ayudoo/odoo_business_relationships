from odoo.http import request
from odoo import fields, models, SUPERUSER_ID


class Page(models.Model):
    _inherit = "website.page"

    group_ids = fields.Many2many(
        "res.groups",
        string="Visible Groups",
        help=(
            "The user needs to be in at least one of these groups for the redirect to"
            + " have effect"
        ),
    )

    def _compute_visible(self):
        super()._compute_visible()
        if self.env.user.id != SUPERUSER_ID:
            for record in self:
                if record.group_ids and record.is_visible:
                    record.is_visible = any(
                        gid in request.env.user.groups_id.ids
                        for gid in record.group_ids.ids
                    )

    def write(self, vals):
        # Unfortunately, get_unique_path does not have the page context
        for page in self:

            website_id = False
            if vals.get('website_id') or page.website_id:
                website_id = vals.get('website_id') or page.website_id.id

            self = self.with_context(page=page)
            super().write(vals)

        return True

    def action_edit_page(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'website.page',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('website_user_types.website_pages_form_view').id,
        }
