# -*- coding: utf-8 -*-
from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, values):
        """Pass on the group_ids so we can assign the default business relationship on the
        partner model.
        """

        if "groups_id" in values:
            self = self.with_context(
                user_group_ids={
                    gid
                    for groups_add in values["groups_id"]
                    for gid in groups_add[2]
                    if groups_add[0] == 6
                }
            )
        record = super().create(values)
        record.partner_id._set_tax_groups()
        return record
