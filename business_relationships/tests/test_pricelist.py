from odoo.addons.business_relationships.tests.common import (
    BusinessRelationshipsTestCommon,
)
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPricelistCompanyProperty(BusinessRelationshipsTestCommon):
    def test_get_partner_pricelist_multi_default_company_behavior(self):
        # ensure different currencies, independently of region
        other_currency = self.env.ref("base.USD").id
        public_pricelist = self.env.ref("product.list0")
        if public_pricelist.currency_id.id == other_currency:
            other_currency = self.env.ref("base.EUR").id

        list_other_currency = self.env["product.pricelist"].create(
            {
                "name": "Other Currency",
                "currency_id": other_currency,
                "sequence": 100,
            }
        )

        # on company creation, the default pricelist is matched by the currency
        company_other_currency = self.env["res.company"].create(
            {
                "name": "Company Other Currency",
                "currency_id": other_currency,
            }
        )

        test_partner_default_company = self.env["res.partner"].create(
            {
                "name": "Georgi",
            }
        )
        self.assertEqual(
            test_partner_default_company.property_product_pricelist, public_pricelist
        )

        self.env.company = company_other_currency
        test_partner_other_company = self.env["res.partner"].create(
            {
                "name": "Max",
            }
        )
        self.assertEqual(
            test_partner_other_company.property_product_pricelist, list_other_currency
        )


@tagged("post_install", "-at_install")
class TestPricelistPartnerProperty(BusinessRelationshipsTestCommon):
    def test_get_partner_pricelist_multi_default_company_behavior(self):
        list_europe = self.env["product.pricelist"].create(
            {
                "name": "Europe",
            }
        )

        test_partner = self.env["res.partner"].create(
            {
                "name": "Georgi",
            }
        )
        self.assertEqual(
            test_partner.property_product_pricelist, self.env.ref("product.list0")
        )

        test_partner_property = self.env["res.partner"].create(
            {"name": "Delyan", "property_product_pricelist": list_europe}
        )
        self.assertEqual(test_partner_property.property_product_pricelist, list_europe)

        test_partner_property2 = self.env["res.partner"].create(
            {
                "name": "Martin",
            }
        )
        self.env["ir.property"]._set_multi(
            "property_product_pricelist",
            "res.partner",
            {test_partner_property2.id: list_europe},
        )
        self.assertEqual(test_partner_property2.property_product_pricelist, list_europe)

    def test_sale_order_shipping_pricelist(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Partner",
                "business_relationship_id": self.business_relationship_b2c_shipping.id,
            }
        )
        public_pricelist = self.env.ref("product.list0")
        self.assertEqual(partner.property_product_pricelist, public_pricelist)

        other_pricelist = self.env["product.pricelist"].create(
            {
                "name": "Other Pricelist",
                "currency_id": self.env.ref("base.EUR").id,
                "sequence": 100,
            }
        )
        shipping = self.env["res.partner"].create(
            {
                "name": "Shipping Address",
                "parent_id": partner.id,
                "property_product_pricelist": other_pricelist.id,
            }
        )

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
            }
        )
        sale_order.partner_shipping_id = shipping
        sale_order.onchange_partner_shipping_id()
        self.assertEqual(sale_order.pricelist_id, other_pricelist)


@tagged("post_install", "-at_install")
class TestPricelist(BusinessRelationshipsTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # public pricelist is fallback/matchall
        cls.env.ref("product.list0").sequence = 99

        cls.benelux = cls.env["res.country.group"].create(
            {
                "name": "BeNeLux",
                "country_ids": [
                    (
                        6,
                        0,
                        (
                            cls.env.ref("base.be")
                            + cls.env.ref("base.lu")
                            + cls.env.ref("base.nl")
                        ).ids,
                    )
                ],
            }
        )

        cls.list_benelux_b2c_internal = cls.env["product.pricelist"].create(
            {
                "name": "Benelux B2C/Internal",
                "country_group_ids": [(4, cls.benelux.id)],
                "business_relationship_ids": [
                    (
                        6,
                        0,
                        [
                            cls.business_relationship_b2c.id,
                            cls.business_relationship_internal.id,
                        ],
                    )
                ],
                "sequence": 1,
            }
        )

        cls.list_benelux = cls.env["product.pricelist"].create(
            {
                "name": "Benelux",
                "country_group_ids": [(4, cls.benelux.id)],
                "sequence": 2,
            }
        )

        cls.list_europe = cls.env["product.pricelist"].create(
            {
                "name": "Europe",
                "country_group_ids": [(4, cls.env.ref("base.europe").id)],
                "sequence": 3,
            }
        )

        cls.list_internal = cls.env["product.pricelist"].create(
            {
                "name": "B2C/Internal",
                "business_relationship_ids": [
                    (6, 0, [cls.business_relationship_internal.id])
                ],
                "sequence": 4,
            }
        )

        cls.list_b2b = cls.env["product.pricelist"].create(
            {
                "name": "Europe",
                "business_relationship_ids": [(4, cls.business_relationship_b2b.id)],
                "sequence": 6,
            }
        )

    def test_get_partner_pricelist_multi_default_behavior(self):
        # As Odoo does not test this itself with explcit test cases,
        # let's test that we do not break it

        # from product/models/product_pricelist
        # First, the pricelist of the specific property (res_id set), this one
        #        is created when saving a pricelist on the partner form view.
        # Else, it will return the pricelist of the partner country group
        # Else, it will return the generic property (res_id not set), this one
        #       is created on the company creation.
        # Else, it will return the first available pricelist

        test_partner_without_country_id = self.env["res.partner"].create(
            {
                "name": "Georgi",
            }
        )
        self.assertEqual(
            test_partner_without_country_id.property_product_pricelist,
            self.env.ref("product.list0"),
        )

        test_partner_germany = self.env["res.partner"].create(
            {"name": "Georg", "country_id": self.env.ref("base.de").id}
        )
        self.assertEqual(
            test_partner_germany.property_product_pricelist, self.list_europe
        )

        test_partner_benelux = self.env["res.partner"].create(
            {"name": "Joris", "country_id": self.env.ref("base.nl").id}
        )
        self.assertEqual(
            test_partner_benelux.property_product_pricelist,
            self.list_benelux_b2c_internal,
        )

    def test_get_partner_pricelist_business_relationship_behavior(self):
        # First match by country and business relationship
        employees_group = self.env.ref("base.group_user")
        user_employee_nl = self._create_user(
            {
                "name": "Georgi",
                "groups_id": [(6, 0, [employees_group.id])],
            }
        )
        user_employee_nl.partner_id.country_id = self.env.ref("base.nl")
        self.assertEqual(
            user_employee_nl.partner_id.property_product_pricelist,
            self.list_benelux_b2c_internal,
        )

        # match by business relationship only
        user_employee = self._create_user(
            {
                "name": "Vladimir",
                "groups_id": [(6, 0, [employees_group.id])],
            }
        )
        self.assertEqual(
            user_employee.partner_id.property_product_pricelist, self.list_internal
        )

        # fallback match by country, because there is no entry for benelux/b2b
        test_partner_benelux = self.env["res.partner"].create(
            {
                "name": "Hugo",
                "country_id": self.env.ref("base.nl").id,
                "business_relationship_id": self.env.ref(
                    "business_relationships.business_relationship_b2b"
                ).id,
            }
        )
        self.assertEqual(
            test_partner_benelux.property_product_pricelist, self.list_benelux
        )

        # match by country only
        test_partner_germany = self.env["res.partner"].create(
            {"name": "Viktor", "country_id": self.env.ref("base.de").id}
        )
        self.assertEqual(
            test_partner_germany.property_product_pricelist, self.list_europe
        )

        # fallback to fallback pricelist
        test_partner_us_b2c = self.env["res.partner"].create(
            {"name": "James", "country_id": self.env.ref("base.us").id}
        )
        self.assertEqual(
            test_partner_us_b2c.property_product_pricelist,
            self.env.ref("product.list0"),
        )
