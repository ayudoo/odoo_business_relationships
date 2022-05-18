# -*- coding: utf-8 -*-
from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def website_domain(self, website_id=False):
        domain = super().website_domain(website_id=website_id)
        group_ids = self.env.context.get("with_group_ids", False)
        if group_ids:
            domain = domain + [
                ('|'),
                ('group_ids', '=', False),
                ('group_ids', 'in', group_ids),
            ]

        return domain

    def sale_product_domain(self):
        domain = super().sale_product_domain()

        if self.user_has_groups("website.group_website_designer"):
            return domain

        # A user having both groups cannot be configured with business relationships,
        # but you can do so in the technical admin user settings
        if self.user_has_groups(
            "website_user_types.group_website_user_type_b2b"
        ) and self.user_has_groups("website_user_types.group_website_user_type_b2c"):
            domain = domain + [
                ("|"),
                ("visible_group_b2c", "=", True),
                ("visible_group_b2b", "=", True),
            ]
        else:
            if self.user_has_groups("website_user_types.group_website_user_type_b2b"):
                domain.append(
                    ("visible_group_b2b", "=", True),
                )
            else:
                domain.append(
                    ("visible_group_b2c", "=", True),
                )

        return domain
