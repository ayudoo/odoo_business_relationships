# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_template(self, template, values=None):
        model = values.get('doc_model', False)
        docs = values.get('docs', False)

        if model == "sale.order" and docs:
            self._validate_same_tax_display_settings(docs.user_id)
            if docs.user_id:
                self = self.with_user(docs.user_id[0])

        elif model == "account.move":
            self._validate_same_tax_display_settings(docs.user_id)
            if docs.user_id:
                self = self.with_user(docs.user_id[0])

        return super()._render_template(template, values=values)

    def _validate_same_tax_display_settings(self, users):
        if len(users) < 2:
            return

        tax_excluded = None
        error_msg = (
            "Cannot print reports for different tax settings together."
            + " Please print them separately."
        )

        for user in users:
            if user.has_group('account.group_show_line_subtotals_tax_excluded'):
                if tax_excluded is None:
                    tax_excluded = True

                if tax_excluded is False:
                    raise UserError(error_msg)

            else:
                if tax_excluded is None:
                    tax_excluded = False

                if tax_excluded is True:
                    raise UserError(error_msg)
