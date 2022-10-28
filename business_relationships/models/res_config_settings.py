from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _reset_business_relationship_dependent_groups(self):
        if self.show_line_subtotals_tax_selection == "tax_excluded":
            tax_included_group = self.env.ref(
                "account.group_show_line_subtotals_tax_included"
            )
            tax_included_group.write({"users": [(5, [])]})
        else:
            tax_excluded_group = self.env.ref(
                "account.group_show_line_subtotals_tax_excluded"
            )
            tax_excluded_group.write({"users": [(5, [])]})

    def _ondelete_business_relationship_dependent(self):
        for record in self:
            record.show_line_subtotals_tax_selection = "tax_excluded"
            record._reset_business_relationship_dependent_groups()
            record._compute_group_show_line_subtotals()
            record.set_values()

    show_line_subtotals_tax_selection = fields.Selection(
        selection_add=[
            ("business_relationship_dependent", "Business Relationship Dependent"),
        ],
        ondelete={
            "business_relationship_dependent": _ondelete_business_relationship_dependent
        },
        # default="tax_excluded",
    )

    def set_values(self):
        tax_selection_changed = False
        current_tax_selection = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "account.show_line_subtotals_tax_selection",
                default="tax_excluded",
            )
        )
        if current_tax_selection != self.show_line_subtotals_tax_selection:
            tax_selection_changed = True
            # Users._check_one_user_type is executed whenever a group is set or removed
            # during super().set_values()
            # This means, when switching away from business_relationship_dependent,
            # first we  need to remove the business relationship dependent groups
            # before super is called
            if current_tax_selection == "business_relationship_dependent":
                self._reset_business_relationship_dependent_groups()

        res = super().set_values()

        if tax_selection_changed:
            # when switching to business_relationship_dependent, there are no more
            # implied tax_selection groups and we need to set the business relationship
            # ones
            if (
                self.show_line_subtotals_tax_selection
                == "business_relationship_dependent"
            ):
                for partner in (
                    self.env["res.partner"].with_context(active_test=False).search([])
                ):
                    partner._set_tax_groups()

        return res

    @api.depends("show_line_subtotals_tax_selection")
    def _compute_group_show_line_subtotals(self):
        # business_relationship_dependent has no implied tax groups for all users
        if self.show_line_subtotals_tax_selection == "business_relationship_dependent":
            self.update(
                {
                    "group_show_line_subtotals_tax_included": False,
                    "group_show_line_subtotals_tax_excluded": False,
                }
            )
        else:
            super()._compute_group_show_line_subtotals()
