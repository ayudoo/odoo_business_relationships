# -*- coding: utf-8 -*-
from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            self._strip_website_user_groups(values)

        records = super().create(values_list)

        for business_relationship in records.business_relationship_id:
            wut = business_relationship.website_user_group_id

            if wut:
                user_ids = records.filtered(
                    lambda r: r.business_relationship_id == business_relationship
                ).ids
                wut.write({"users": [
                    (4, uid)
                    for uid in user_ids
                ]})

        return records

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
