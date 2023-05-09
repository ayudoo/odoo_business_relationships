from odoo.addons.business_relationships.tests.common import (
    BusinessRelationshipsTestUsers,
)


class TestFiscalPosition(BusinessRelationshipsTestUsers):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.be = cls.env.ref("base.be")
        cls.us = cls.env.ref("base.us")

        cls.fp = cls.env["account.fiscal.position"]
        # reset any existing FP
        cls.fp.search([]).write({"auto_apply": False})

        cls.de_b2c = cls.fp.create(
            {
                "name": "DE B2C",
                "business_relationship_ids": [
                    (6, 0, [cls.business_relationship_b2c.id])
                ],
                "auto_apply": True,
                "country_id": cls.de.id,
                "vat_required": False,
                "sequence": 2,
            }
        )
        cls.bg_b2c = cls.fp.create(
            {
                "name": "BG B2C",
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
                "auto_apply": True,
                "country_id": cls.bg.id,
                "vat_required": False,
                "sequence": 3,
            }
        )
        cls.bg_b2b = cls.fp.create(
            {
                "name": "BG B2B",
                "business_relationship_ids": [
                    (6, 0, [cls.business_relationship_b2b.id])
                ],
                "auto_apply": True,
                "country_id": cls.bg.id,
                "vat_required": True,
                "sequence": 4,
            }
        )
        cls.europe_b2c = cls.fp.create(
            {
                "name": "EU B2C",
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
                "auto_apply": True,
                "country_group_id": cls.env.ref("base.europe").id,
                "vat_required": False,
                "sequence": 7,
            }
        )
        cls.europe_b2b_without_vat = cls.fp.create(
            {
                "name": "EU B2B without VAT",
                "business_relationship_ids": [
                    (6, 0, [cls.business_relationship_b2b.id])
                ],
                "auto_apply": True,
                "country_group_id": cls.env.ref("base.europe").id,
                "vat_required": False,
                "sequence": 8,
            }
        )
        cls.europe_b2b = cls.fp.create(
            {
                "name": "EU B2B with VAT",
                "business_relationship_ids": [
                    (6, 0, [cls.business_relationship_b2b.id])
                ],
                "auto_apply": True,
                "country_group_id": cls.env.ref("base.europe").id,
                "vat_required": True,
                "sequence": 9,
            }
        )
        cls.fallback = cls.fp.create(
            {
                "name": "Fallback position",
                "auto_apply": True,
                "sequence": 10,
            }
        )

        cls.user_portal_de = cls._create_portal_user(
            {
                "name": "Micha",
                "country_id": cls.de.id,
            }
        )
        cls.user_company_de = cls._create_portal_user(
            {
                "name": "Ein Mü without VAT",
                "is_company": True,
                "country_id": cls.de.id,
            }
        )
        cls.user_company_be = cls._create_portal_user(
            {
                "name": "Hugo",
                "is_company": True,
                "country_id": cls.be.id,
                "vat": "BE0477472701",
            }
        )
        cls.user_portal_us = cls._create_portal_user(
            {
                "name": "James",
                "country_id": cls.us.id,
            }
        )

    def test_get_fiscal_position_with_business_relationship_filters(self):
        def assert_fp(partner_or_user, expected_pos, message):
            partner = partner_or_user
            if partner._name == "res.users":
                partner = partner.partner_id

            self.assertEqual(
                self.fp._get_fiscal_position(partner).id, expected_pos.id, message
            )

        assert_fp(
            self.user_portal, self.bg_b2c, "Portal user should match BG B2C position"
        )
        assert_fp(
            self.user_company, self.bg_b2b, "Company should match BG B2B position"
        )
        assert_fp(
            self.user_supplier,
            self.europe_b2b_without_vat,
            "Portal supplier should match EU B2B without VAT position",
        )
        assert_fp(
            self.user_employee, self.bg_b2c, "Employee should match BG B2C position"
        )
        assert_fp(
            self.user_account_invoice,
            self.europe_b2c,
            "Sales Manager should match EU B2C position",
        )

        assert_fp(
            self.user_portal_de,
            self.de_b2c,
            "Portal user DE should match DE B2C position",
        )

        self.assertGreater(
            self.europe_b2b.sequence, self.europe_b2b_without_vat.sequence
        )
        assert_fp(
            self.user_company_de,
            self.europe_b2b_without_vat,
            "Company DE without VAT should match EU B2B wihtout VAT position",
        )
        assert_fp(
            self.user_company_be,
            self.europe_b2b,
            "Company BE should match EU B2B position",
        )

        assert_fp(
            self.user_portal_us,
            self.fallback,
            "Portal user US should match fallback position",
        )
