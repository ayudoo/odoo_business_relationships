# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import api, models, fields, SUPERUSER_ID


class Page(models.Model):
    _inherit = "website.page"

    group_ids = fields.Many2many(
        "res.groups",
        string="Visible Groups",
        help="The user needs to be in at least one of these groups for the redirect to have effect",
    )

    def _compute_visible(self):
        super()._compute_visible()
        if self.env.user.id != SUPERUSER_ID:
            for record in self:
                if record.group_ids and record.is_visible:
                    record.is_visible = (
                        record.group_ids.ids in request.env.user.groups_id.ids
                    )
