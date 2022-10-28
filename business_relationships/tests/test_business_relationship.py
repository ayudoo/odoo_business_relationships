from odoo.tests import tagged
from odoo.addons.business_relationships.tests.common import (
    BusinessRelationshipsTestUsers,
)


@tagged("post_install", "-at_install")
class TestBusinessRelationship(BusinessRelationshipsTestUsers):
    def test_switch_b2b2tax_included(self):
        tax_excluded = "account.group_show_line_subtotals_tax_excluded"
        tax_included = "account.group_show_line_subtotals_tax_included"

        config = self.env["res.config.settings"].create({})
        config.show_line_subtotals_tax_selection = "business_relationship_dependent"
        config._compute_group_show_line_subtotals()
        config.flush_model()
        config.execute()

        # defaults
        # self.assertEqual(self.user_portal.has_group(tax_included), True)
        # self.assertEqual(self.user_company.has_group(tax_excluded), True)
        # self.assertEqual(self.user_supplier.has_group(tax_excluded), True)

        self.business_relationship_b2b.show_line_subtotals_tax_selection = (
            "tax_included"
        )

        # test it remains unchanged
        self.assertEqual(self.user_portal.has_group(tax_included), True)
        # test added and removed groups
        self.assertEqual(self.user_company.has_group(tax_excluded), False)
        self.assertEqual(self.user_supplier.has_group(tax_excluded), False)
        self.assertEqual(self.user_company.has_group(tax_included), True)
        self.assertEqual(self.user_supplier.has_group(tax_included), True)

    def test_switch_b2c2tax_excluded(self):
        tax_excluded = "account.group_show_line_subtotals_tax_excluded"
        tax_included = "account.group_show_line_subtotals_tax_included"

        config = self.env["res.config.settings"].create({})
        config.show_line_subtotals_tax_selection = "business_relationship_dependent"
        config._compute_group_show_line_subtotals()
        config.flush_model()
        config.execute()

        # defaults
        # self.assertEqual(self.user_employee.has_group(tax_included), True)
        # self.assertEqual(self.user_portal.has_group(tax_included), True)

        self.business_relationship_b2c.show_line_subtotals_tax_selection = (
            "tax_excluded"
        )

        # test it remains unchanged
        self.assertEqual(self.user_employee.has_group(tax_included), False)
        self.assertEqual(self.user_employee.has_group(tax_excluded), True)
        # test added and removed groups
        self.assertEqual(self.user_portal.has_group(tax_included), False)
        self.assertEqual(self.user_portal.has_group(tax_excluded), True)

    def test_switch_internal2tax_included(self):
        tax_excluded = "account.group_show_line_subtotals_tax_excluded"
        tax_included = "account.group_show_line_subtotals_tax_included"

        config = self.env["res.config.settings"].create({})
        config.show_line_subtotals_tax_selection = "business_relationship_dependent"
        config._compute_group_show_line_subtotals()
        config.flush_model()
        config.execute()

        # defaults
        # self.assertEqual(self.user_supplier.has_group(tax_excluded), True)
        # self.assertEqual(self.user_employee.has_group(tax_included), True)
        self.assertEqual(self.user_odoo_root.has_group(tax_excluded), True)

        self.business_relationship_internal.show_line_subtotals_tax_selection = (
            "tax_included"
        )

        # test it remains unchanged
        self.assertEqual(self.user_supplier.has_group(tax_excluded), True)
        # test added and removed groups
        self.assertEqual(self.user_employee.has_group(tax_excluded), False)
        self.assertEqual(self.user_employee.has_group(tax_included), True)
        self.assertEqual(self.user_odoo_root.has_group(tax_excluded), False)
        self.assertEqual(self.user_odoo_root.has_group(tax_included), True)
