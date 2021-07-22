# -*- coding: utf-8 -*-
from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, values):
        res = super().create(values)

        if res.partner_id and res.partner_id.business_relationship_id:
            website_user_group = res.partner_id.business_relationship_id.website_user_group_id
            if website_user_group:
                website_user_group.write({"users": [(4, res.id)]})

        return res

    @api.model
    def get_user_website_user_group_class(self):
        if self.user_has_groups("account.group_show_line_subtotals_tax_included"):
            wut_class = "wut_tax_included"
        else:
            wut_class = "wut_tax_excluded"

        if self.user_has_groups("website_user_types.group_website_user_type_b2b"):
            return "{} wut_group_b2b".format(wut_class)
        if self.user_has_groups("website_user_types.group_website_user_type_b2c"):
            return "{} wut_group_b2c".format(wut_class)
        return wut_class
