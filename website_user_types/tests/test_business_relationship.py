from odoo.addons.business_relationships.tests.common import (
    BusinessRelationshipsTestUsers,
)


class TestBusinessRelationship(BusinessRelationshipsTestUsers):
    def test_default_website_user_group(self):
        group_b2b = self.env.ref("website_user_types.group_b2b")
        group_b2c = self.env.ref("website_user_types.group_b2c")

        self.assertEqual(
            self.business_relationship_b2b.website_user_group_id, group_b2b
        )
        self.assertEqual(
            self.business_relationship_b2c.website_user_group_id, group_b2c
        )
        self.assertEqual(
            self.business_relationship_internal.website_user_group_id, group_b2c
        )

    def test_change_website_user_group(self):
        group_b2b = "website_user_types.group_b2b"
        group_b2c = "website_user_types.group_b2c"

        # check default to fail fast
        self.assertEqual(self.user_portal.has_group(group_b2c), True)

        self.business_relationship_b2c.website_user_group_id = self.env.ref(group_b2b)

        self.assertEqual(self.user_portal.has_group(group_b2b), True)
        self.assertEqual(self.user_portal.has_group(group_b2c), False)

        self.business_relationship_b2b.website_user_group_id = self.env.ref(group_b2c)

        self.assertEqual(self.user_company.has_group(group_b2c), True)
        self.assertEqual(self.user_supplier.has_group(group_b2c), True)
        self.assertEqual(self.user_company.has_group(group_b2b), False)
        self.assertEqual(self.user_supplier.has_group(group_b2b), False)
