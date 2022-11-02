from odoo import api, fields, models


class BusinessRelationship(models.Model):
    _name = "res.partner.business_relationship"
    _inherit = ["res.partner.business_relationship"]

    update_prices = fields.Boolean(
        string="Update Prices on Login/Address Change",
        required=True,
        default=True,
        help="By default, Odoo does not change pricelists or recalculate prices on"
        + " address or login changes. With this option, pricelists and prices will be"
        + " updated according to configuration. This option may conflict with Geo IP.",
    )

    def _get_default_website_user_group(self):
        return self.env.ref(
            "website_user_types.group_b2b",
            raise_if_not_found=False,
        )

    def _website_user_group_domain(self):
        category_id = self.env.ref(
            "website_user_types.module_category_website_user_types",
            raise_if_not_found=False,
        )
        if category_id:
            return [("category_id", "=", category_id.id)]
        else:
            return []

    website_user_group_id = fields.Many2one(
        "res.groups",
        "Website User Type",
        help=(
            "Use this field to assign an access group to login users associated with"
            + " this partner"
        ),
        default=_get_default_website_user_group,
        domain=_website_user_group_domain,
    )

    @api.model_create_multi
    def create(self, values_list):
        records = super().create(values_list)

        for record in records:
            if record.website_user_group_id:
                record._update_users_website_user_group(
                    None, record.website_user_group_id,
                )

        return records

    def write(self, values):
        old_website_user_group = self.website_user_group_id
        super().write(values)
        new_website_user_group_id = values.get("website_user_group_id", False)
        if "website_user_group_id" in values:
            new_website_user_group = None
            if new_website_user_group_id:
                new_website_user_group = self.env["res.groups"].browse(
                    new_website_user_group_id
                )
            self._update_users_website_user_group(
                old_website_user_group, new_website_user_group
            )

    def _update_users_website_user_group(self, old_value, new_value):
        if old_value == new_value:
            return
        if old_value and old_value.users:
            old_value.write(
                {"users": [(6, 0, set(old_value.users.ids) - set(self.user_ids.ids))]}
            )
        if new_value:
            if self.user_ids.ids:
                user_ids = new_value.users.ids + self.user_ids.ids
                new_value.write({"users": [(6, 0, user_ids)]})

    @api.model
    def _init_website_user_groups(self):
        group_b2c = self.env.ref("website_user_types.group_b2c")
        group_b2b = self.env.ref("website_user_types.group_b2b")
        internal = self.env.ref("business_relationships.business_relationship_internal")

        for business_relationship in self.env[
            "res.partner.business_relationship"
        ].search([("website_user_group_id", "=", False)]):
            if (
                business_relationship == internal
                or "b2c" in business_relationship.name.lower()
            ):
                business_relationship.website_user_group_id = group_b2c.id
            else:
                business_relationship.website_user_group_id = group_b2b.id
