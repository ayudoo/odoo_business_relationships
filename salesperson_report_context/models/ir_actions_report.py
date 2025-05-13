from odoo import models
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_template(self, template, values=None):
        model = values.get("doc_model", False)
        docs = values.get("docs", False)

        if model == "sale.order" and docs:
            if docs.user_id:
                self = self.with_user(docs.user_id[0])

        elif model == "account.move" and docs:
            if docs.user_id:
                self = self.with_user(docs.user_id[0])

        return super()._render_template(template, values=values)