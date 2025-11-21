from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    visible_group_b2c = fields.Boolean(
        "Visible Group B2C",
        default=True,
    )
    visible_group_b2b = fields.Boolean(
        "Visible Group B2B",
        default=True,
    )

    def _compute_has_hidden_groups(self):
        groups = self.env["res.groups"].search(
            [
                ('id', 'not in', [
                    self.env.ref('website_user_types.group_b2b').id,
                    self.env.ref('website_user_types.group_b2c').id,
                ]),
                ('category_id', '=', self.env.ref("website_user_types.module_category_website_user_types").id),
            ]
        )
        has_groups = bool(groups)

        for record in self:
            record.has_hidden_groups = has_groups

    has_hidden_groups = fields.Boolean(compute=_compute_has_hidden_groups)

    hidden_for_group_ids = fields.Many2many(
        "res.groups",
        string="Hidden for Groups",
        domain=lambda self: [
            ('id', 'not in', [
                self.env.ref('website_user_types.group_b2b').id,
                self.env.ref('website_user_types.group_b2c').id,
            ]),
            ('category_id', '=', self.env.ref(
                "website_user_types.module_category_website_user_types"
            ).id),
        ],
    )

    def can_access_from_current_website(self, **kwargs):
        can_access = super().can_access_from_current_website(**kwargs)

        if can_access:
            if self.env.user.has_group("website.group_website_designer"):
                return can_access

            if self.env.user.has_group(
                "website_user_types.group_b2b"
            ) and self.env.user.has_group(
                "website_user_types.group_b2c"
            ):
                return self.visible_group_b2c or self.visible_group_b2b
            elif self.env.user.has_group("website_user_types.group_b2b"):
                return self.visible_group_b2b
            elif self.env.user.has_group("website_user_types.group_b2c"):
                return self.visible_group_b2c
            elif not self.hidden_for_group_ids:
                return True
            else:
                for group in self.hidden_for_group_ids:
                    self._cr.execute(
                        "SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid=%s",
                        (self._uid, group.id),
                    )
                    if bool(self._cr.fetchone()):
                        return False

                return True

        return can_access
