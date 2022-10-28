from odoo.tests.common import TransactionCase


class BusinessRelationshipsTestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.business_relationship_b2b = cls.env.ref(
            "business_relationships.business_relationship_b2b"
        )
        cls.business_relationship_b2c = cls.env.ref(
            "business_relationships.business_relationship_b2c"
        )
        cls.business_relationship_b2c_shipping = cls.business_relationship_b2c.copy()
        cls.business_relationship_b2c_shipping.name = "B2C individual"
        cls.business_relationship_b2c_shipping.child_contact_pricelist = "individual"
        cls.business_relationship_b2c_shipping.update_pricelist_by = "shipping"

        cls.business_relationship_internal = cls.env.ref(
            "business_relationships.business_relationship_internal"
        )
        cls.payment_term = cls.env.ref("account.account_payment_term_30days")

    @classmethod
    def _create_user(cls, values):
        assert "name" in values
        token = values["name"].lower().strip()
        if "login" not in values:
            values["login"] = token
        if "email" not in values:
            values["email"] = token + "@example.com"
        return cls.env["res.users"].with_context(no_reset_password=True).create(values)


class BusinessRelationshipsTestUsers(BusinessRelationshipsTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bg = cls.env.ref("base.bg")
        cls.de = cls.env.ref("base.de")
        cls.us = cls.env.ref("base.us")

        cls.user_odoo_root = cls.env.ref("base.user_root")
        cls.user_portal = cls._create_portal_user(
            {
                "name": "Georgi",
                "country_id": cls.bg.id,
            }
        )
        cls.user_company = cls._create_portal_user(
            {
                "name": "4udesno Ltd",
                "is_company": True,
                "country_id": cls.bg.id,
                "vat": "BG0477472701",
            }
        )
        cls.user_supplier = cls._create_portal_user(
            {
                "name": "Martinka",
                "property_supplier_payment_term_id": cls.payment_term,
                "country_id": cls.bg.id,
            }
        )

        employees_group = cls.env.ref("base.group_user")
        cls.user_employee = cls._create_user(
            {
                "name": "Vladimir",
                "groups_id": [(6, 0, [employees_group.id])],
                "country_id": cls.bg.id,
            }
        )

        # test a group that implies group_user
        account_invoice_group = cls.env.ref("account.group_account_invoice")
        cls.user_account_invoice = cls._create_user(
            {
                "name": "Boyan",
                "groups_id": [(6, 0, [account_invoice_group.id])],
                "country_id": cls.de.id,
            }
        )

    @classmethod
    def _create_portal_user(cls, values):
        assert "name" in values
        token = values["name"].lower().strip()
        if "email" not in values:
            values["email"] = token + "@example.com"

        partner = cls.env["res.partner"].create(values)
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            ._create_user_from_template(
                {
                    "email": partner.email,
                    "login": partner.email,
                    "partner_id": partner.id,
                }
            )
        )

    def get_users(self):
        return [
            getattr(self, i)
            for i in dir(self)
            if i.startswith("user_") and not callable(getattr(self, i))
        ]

    def _assert_every_user_has_group(self, group, expectation):
        for user in self.get_users():
            self.assertEqual(
                user.has_group(group),
                expectation,
                "{} ({}) has group {}: {}".format(
                    user.partner_id.business_relationship_id.display_name,
                    user.display_name,
                    group,
                    expectation,
                ),
            )
