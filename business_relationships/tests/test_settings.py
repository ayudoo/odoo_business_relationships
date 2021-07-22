# -*- coding: utf-8 -*-
from odoo.addons.business_relationships.tests.common import BusinessRelationshipsTestUsers


class TestSettings(BusinessRelationshipsTestUsers):
    def _assert_business_relationship_dependent_groups(self):
        tax_excluded = "account.group_show_line_subtotals_tax_excluded"
        tax_included = "account.group_show_line_subtotals_tax_included"

        self.assertEqual(self.user_portal.has_group(tax_excluded), False)
        self.assertEqual(self.user_company.has_group(tax_excluded), True)
        self.assertEqual(self.user_supplier.has_group(tax_excluded), True)
        self.assertEqual(self.user_employee.has_group(tax_excluded), False)
        self.assertEqual(self.user_account_invoice.has_group(tax_excluded), False)

        self.assertEqual(self.user_portal.has_group(tax_included), True)
        self.assertEqual(self.user_company.has_group(tax_included), False)
        self.assertEqual(self.user_supplier.has_group(tax_included), False)
        self.assertEqual(self.user_employee.has_group(tax_included), True)
        self.assertEqual(self.user_account_invoice.has_group(tax_included), True)

    def test_switch_tax_excluded_tax_business_relationship(self):
        self._assert_every_user_has_group(
            "account.group_show_line_subtotals_tax_excluded", True
        )
        self._assert_every_user_has_group(
            "account.group_show_line_subtotals_tax_included", False
        )

        config = self.env["res.config.settings"].create({})
        config.show_line_subtotals_tax_selection = "business_relationship_dependent"
        config._onchange_sale_tax()
        config.flush()
        config.execute()
        self._assert_business_relationship_dependent_groups()

        config.show_line_subtotals_tax_selection = "tax_excluded"
        config._onchange_sale_tax()
        config.flush()
        config.execute()

        self._assert_every_user_has_group(
            "account.group_show_line_subtotals_tax_excluded", True
        )
        self._assert_every_user_has_group(
            "account.group_show_line_subtotals_tax_included", False
        )

    def test_switch_tax_included_tax_business_relationship(self):
        config = self.env["res.config.settings"].create({})
        config.show_line_subtotals_tax_selection = "tax_included"
        config._onchange_sale_tax()
        config.flush()
        config.execute()

        config.show_line_subtotals_tax_selection = "business_relationship_dependent"
        config._onchange_sale_tax()
        config.flush()
        config.execute()
        self._assert_business_relationship_dependent_groups()

        config.show_line_subtotals_tax_selection = "tax_included"
        config._onchange_sale_tax()
        config.flush()
        config.execute()

        self._assert_every_user_has_group(
            "account.group_show_line_subtotals_tax_excluded", False
        )
        self._assert_every_user_has_group(
            "account.group_show_line_subtotals_tax_included", True
        )
