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

    def can_access_from_current_website(self, **kwargs):
        can_access = super().can_access_from_current_website(**kwargs)

        if can_access:
            if self.user_has_groups("website.group_website_designer"):
                return can_access

            if self.user_has_groups(
                "website_user_types.group_b2b"
            ) and self.user_has_groups(
                "website_user_types.group_b2c"
            ):
                return self.visible_group_b2c or self.visible_group_b2b
            elif self.user_has_groups("website_user_types.group_b2b"):
                return self.visible_group_b2b
            else:
                return self.visible_group_b2c

        return can_access
