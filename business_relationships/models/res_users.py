from odoo import api, models


class Users(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, values_list):
        # we cannot know all custom modules, installation order and all group
        # configurations.
        # Furthermore, not using model_create_multi notably slows down bulk create.
        # So, we fix the business relationship of the associated partner
        # after user creation.
        users = super().create(values_list)
        for user, values in zip(users, values_list):
            # the partner used to exist and we keep his business relationship
            if values.get("partner_id", False):
                continue

            partner = user.partner_id
            if partner:
                if user.has_group("base.group_user"):
                    partner = partner.with_context(
                        business_relationship_internal_user=True
                    )
                default_br = partner._get_default_business_relationship()
                if default_br and default_br != partner.business_relationship_id:
                    partner.business_relationship_id = default_br
        return users
