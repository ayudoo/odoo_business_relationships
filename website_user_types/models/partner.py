from odoo import models


class Partner(models.Model):
    _inherit = ["res.partner"]
    _name = "res.partner"

    def _after_business_relationship_changed(self):
        super()._after_business_relationship_changed()
        self._set_website_user_groups()

    def _set_website_user_groups(self):
        website_user_groups = self.env["res.groups"].get_website_user_type_groups()

        for record in self:
            if not record.business_relationship_id:
                continue

            group = self.business_relationship_id.website_user_group_id

            if not group:
                continue

            for user_id in self.with_context(active_test=False).user_ids:
                for website_user_group in website_user_groups:
                    if website_user_group == group:
                        website_user_group.write({"users": [(4, user_id.id)]})
                    else:
                        website_user_group.with_context(active_test=False).write(
                            {"users": [(3, user_id.id)]}
                        )
