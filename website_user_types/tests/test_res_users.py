from odoo.addons.business_relationships.tests.common import (
    BusinessRelationshipsTestCommon,
)


class TestUsers(BusinessRelationshipsTestCommon):
    def test_default_business_relationship_from_template(self):
        values = {
            "name": "B2C",
            "login": True,
        }
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            ._create_user_from_template(values)
        )

        self.assertTrue(user.has_group("base.group_portal"))
        self.assertEqual(
            user.partner_id.business_relationship_id,
            self.business_relationship_b2c,
        )
