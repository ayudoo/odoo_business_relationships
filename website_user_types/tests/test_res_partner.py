# -*- coding: utf-8 -*-

from odoo.addons.business_relationships.tests.common import BusinessRelationshipsTestUsers


class TestPartner(BusinessRelationshipsTestUsers):
    def test_public_user(self):
        group_b2b = "website_user_types.group_website_user_type_b2b"
        group_b2c = "website_user_types.group_website_user_type_b2c"

        public_user = self.env.ref("base.public_user")
        self.assertEqual(public_user.has_group(group_b2c), True)
        self.assertEqual(public_user.has_group(group_b2b), False)

    def test_switch_business_relationship(self):
        group_b2b = "website_user_types.group_website_user_type_b2b"
        group_b2c = "website_user_types.group_website_user_type_b2c"

        # defaults
        self.assertEqual(self.user_portal.has_group(group_b2c), True)
        self.assertEqual(self.user_company.has_group(group_b2b), True)
        self.assertEqual(self.user_supplier.has_group(group_b2b), True)

        self.user_portal.partner_id.business_relationship_id = self.business_relationship_b2b

        self.assertEqual(self.user_portal.has_group(group_b2b), True)
        self.assertEqual(self.user_portal.has_group(group_b2c), False)

        self.user_company.partner_id.business_relationship_id = self.business_relationship_b2c

        self.assertEqual(self.user_company.has_group(group_b2c), True)
        self.assertEqual(self.user_company.has_group(group_b2b), False)
