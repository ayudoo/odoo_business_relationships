from collections import defaultdict

from odoo import api, Command, models
from odoo.addons.base.models.res_users import name_selection_groups


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
                wut.write({"users": [(4, uid) for uid in user_ids]})

        return records

    def _strip_website_user_groups(self, values):
        # the template user will have a wut group that we need to filter
        # TODO consider to implement different template users according to br
        wut_ids = (
            self.env["res.partner.business_relationship"]
            .search([])
            .website_user_group_id.ids
        )

        group_id = values.get("groups_id", [])
        if group_id:
            for rels in group_id:
                if rels[0] == 6:
                    for wut_id in wut_ids:
                        if wut_id in rels[2]:
                            rels[2].remove(wut_id)

    # alternative solution, works only when changing one user
    # def _remove_reified_groups(self, values):
    #     # UsersImplied of odoo base clears all groups for portal users
    #     result = super()._remove_reified_groups(values)
    #     if len(self) == 1 and result.get("groups_id"):
    #         user_gid = self.partner_id.business_relationship_id.website_user_group_id.id
    #         if isinstance(result["groups_id"], list):
    #             result["groups_id"].append(Command.link(user_gid))
    #         else:
    #             result["groups_id"] |= self.env["res.groups"].browse(user_gid)
    #     return result

    def write(self, values):
        wut_groups = self.env["res.groups"].get_all_website_user_type_groups()
        wut_group_field_name = name_selection_groups(wut_groups.ids)

        if not values.get(wut_group_field_name):
            # UsersImplied will remove all groups from demoted users. So, we have to restore the wut
            users_before = self.filtered(lambda u: u._is_internal())
            res = super().write(values)
            demoted_users = users_before.filtered(lambda u: not u._is_internal())
            demoted_users_map = defaultdict(lambda: self.env["res.users"])

            for duser in demoted_users:
                uwut = duser.partner_id.business_relationship_id.website_user_group_id
                if uwut:
                    demoted_users_map[uwut.id] |= duser

            for uwut_id, dusers in demoted_users_map.items():
                vals = {'groups_id': [Command.link(uwut_id)]}
                if values.get("groups_id"):
                    vals["groups_id"] += values['groups_id']
                super(Users, dusers).write(vals)

            return res

        res = super().write(values)

        # remove other wut groups
        # TODO unless implied
        wut_groups = wut_groups.filtered(lambda w: w.id != values[wut_group_field_name])
        wut_groups.with_context(active_test=False).write(
            {"users": [
                (3, uid)
                for uid in self.ids
            ]}
        )
        return res


class Groups(models.Model):
    _inherit = 'res.groups'

    def get_website_user_type_class(self):
        if self == self.env.ref("website_user_types.group_b2b"):
            return "wut_group_b2b"
        elif self == self.env.ref("website_user_types.group_b2c"):
            return "wut_group_b2c"
        else:
            return "wut_group_{}".format(self.id)

    @api.model
    def get_all_website_user_type_groups(self):
        wut_category = self.env.ref(
            "website_user_types.module_category_website_user_types"
        )
        return self.env["res.groups"].sudo().search([
            ("category_id", "=", wut_category.id)
        ])

    @api.model
    def get_website_user_type_groups(self):
        # we only return groups in use and in the order of their first occurrence
        # in the business relationship
        brs = self.env["res.partner.business_relationship"].search([])
        return brs.website_user_group_id

    @api.model
    def _wut_get_selectable_groups(self):
        # we need to restrict this because of caching reasons
        return (
            self.env.ref("base.group_user")
            + self.get_website_user_type_groups()
            + self.env.ref("base.group_public")
        )
