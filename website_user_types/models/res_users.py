# -*- coding: utf-8 -*-
from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, values):
        self._strip_website_user_groups(values)
        res = super().create(values)

        if res.partner_id and res.partner_id.business_relationship_id:
            website_user_group = (
                res.partner_id.business_relationship_id.website_user_group_id
            )
            if website_user_group:
                website_user_group.write({"users": [(4, res.id)]})

        return res

    def _strip_website_user_groups(self, values):
        # the template user will have a wut group that we need to filter
        # TODO consider to implement different template users according to br
        wut_ids = self.env["res.partner.business_relationship"].search(
            []
        ).website_user_group_id.ids

        group_id = values.get("groups_id", [])
        if group_id:
            for rels in group_id:
                if rels[0] == 6:
                    for wut_id in wut_ids:
                        if wut_id in rels[2]:
                            rels[2].remove(wut_id)

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
