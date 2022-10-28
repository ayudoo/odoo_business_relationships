import base64
import io

from PIL import Image
from odoo.addons.business_relationships.tests.common import (
    BusinessRelationshipsTestUsers,
)


class TestPartner(BusinessRelationshipsTestUsers):
    def test_default_business_relationship(self):
        def assert_business_relationship(user, ct):
            self.assertEqual(user.partner_id.business_relationship_id, ct)

        assert_business_relationship(
            self.user_odoo_root, self.business_relationship_internal
        )
        assert_business_relationship(self.user_portal, self.business_relationship_b2c)
        assert_business_relationship(self.user_company, self.business_relationship_b2b)
        assert_business_relationship(self.user_supplier, self.business_relationship_b2b)
        assert_business_relationship(
            self.user_employee, self.business_relationship_internal
        )
        assert_business_relationship(
            self.user_account_invoice, self.business_relationship_internal
        )

        public_user = self.env.ref("base.public_user")
        assert_business_relationship(public_user, self.business_relationship_b2c)

    def test_fallback_default_business_relationship(self):
        self.business_relationship_internal.active = False
        test_user = self._create_user({"name": "Vasi"})
        self.assertEqual(
            test_user.partner_id.business_relationship_id,
            self.business_relationship_b2c,
        )

        self.business_relationship_b2c.active = False
        self.business_relationship_b2c_shipping.active = False
        test_user = self._create_user({"name": "Vanya"})
        self.assertEqual(
            test_user.partner_id.business_relationship_id,
            self.business_relationship_b2b,
        )

    def test_child_business_relationship(self):
        child_contact = self.env["res.partner"].create(
            {
                "name": "Company Contact",
                "parent_id": self.user_company.partner_id.id,
            }
        )
        self.assertEqual(
            child_contact.business_relationship_id, self.business_relationship_b2b
        )

        self.assertEqual(len(self.user_supplier.partner_id.child_ids), 0)
        self.user_supplier.partner_id.child_ids = [
            (
                0,
                0,
                {
                    "name": "Supplier Contact",
                },
            )
        ]
        self.assertEqual(len(self.user_supplier.partner_id.child_ids), 1)
        child_contact = self.user_supplier.partner_id.child_ids[0]
        self.assertEqual(
            child_contact.business_relationship_id, self.business_relationship_b2b
        )

    def test_change_parent_business_relationship(self):
        child_contact = self.env["res.partner"].create(
            {
                "name": "Company Contact",
                "parent_id": self.user_company.partner_id.id,
            }
        )
        self.assertEqual(
            child_contact.business_relationship_id, self.business_relationship_b2b
        )

        self.user_company.partner_id.business_relationship_id = (
            self.business_relationship_b2c
        )
        self.assertEqual(
            child_contact.business_relationship_id, self.business_relationship_b2c
        )

    def test_assign_default_image(self):
        color_black = "#000000"
        f = io.BytesIO()
        Image.new("RGB", (1920, 1080), color_black).save(f, "JPEG")
        f.seek(0)
        black_image = base64.b64encode(f.read())

        business_relationship_with_image = self.env[
            "res.partner.business_relationship"
        ].create(
            {
                "name": "Business Relationship with Image",
                "image_1920": black_image,
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Stanis",
                "business_relationship_id": business_relationship_with_image.id,
            }
        )
        self.assertEqual(
            partner.image_1920, business_relationship_with_image.image_1920
        )

    def test_individual_child_contact_pricelist(self):
        Pricelist = self.env["product.pricelist"]
        # put it after the sub pricelist, so we check country prevalence
        pricelist_main = Pricelist.create(
            {
                "name": "Main Pricelist",
                "country_group_ids": [self.env.ref("base.europe").id],
                "sequence": 1,
                "business_relationship_ids": [
                    self.business_relationship_b2c.id,
                    self.business_relationship_b2c_shipping.id,
                    self.business_relationship_b2b.id,
                ],
            }
        )
        pricelist_sub = Pricelist.create(
            {
                "name": "Sub Pricelist",
                "sequence": 0,
                "business_relationship_ids": [
                    self.business_relationship_b2c.id,
                    self.business_relationship_b2c_shipping.id,
                    self.business_relationship_b2b.id,
                ],
            }
        )

        user = self.env["res.partner"].create(
            {
                "name": "B2C User",
                "country_id": self.bg.id,
                "business_relationship_id": self.business_relationship_b2c_shipping.id,
            }
        )
        self.assertEqual(user.property_product_pricelist, pricelist_main)
        shipping = self.env["res.partner"].create(
            {
                "name": "Shipping Address US",
                "country_id": self.us.id,
                "parent_id": user.id,
                "type": "delivery",
            }
        )
        self.assertEqual(shipping.property_product_pricelist, pricelist_sub)

        # Default behavior, contacts share the same pricelist with their parent
        user = self.env["res.partner"].create(
            {
                "name": "B2B User",
                "country_id": self.bg.id,
                "business_relationship_id": self.business_relationship_b2b.id,
            }
        )
        self.assertEqual(user.property_product_pricelist, pricelist_main)
        shipping = self.env["res.partner"].create(
            {
                "name": "Shipping Address US",
                "country_id": self.us.id,
                "parent_id": user.id,
                "type": "delivery",
            }
        )
        self.assertEqual(shipping.property_product_pricelist, pricelist_main)

    def test_change_tax_display_according_to_business_relationship_change(self):
        tax_excluded = "account.group_show_line_subtotals_tax_excluded"
        tax_included = "account.group_show_line_subtotals_tax_included"

        config = self.env["res.config.settings"].create({})
        config.show_line_subtotals_tax_selection = "business_relationship_dependent"
        config._compute_group_show_line_subtotals()
        config.flush_model()
        config.execute()

        self.user_portal.business_relationship_id = self.business_relationship_b2b
        self.user_company.business_relationship_id = self.business_relationship_b2c
        self.user_odoo_root.business_relationship_id = self.business_relationship_b2c

        self.assertEqual(self.user_portal.has_group(tax_included), False)
        self.assertEqual(self.user_portal.has_group(tax_excluded), True)

        self.assertEqual(self.user_company.has_group(tax_excluded), False)
        self.assertEqual(self.user_company.has_group(tax_included), True)

        # and for inactive user
        self.assertEqual(self.user_odoo_root.has_group(tax_excluded), False)
        self.assertEqual(self.user_odoo_root.has_group(tax_included), True)
