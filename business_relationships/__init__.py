from odoo import api, SUPERUSER_ID
from . import models, report


def init_partner_business_relationships(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"]._init_partner_business_relationships()


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    tax_selection_param = (
        env["ir.config_parameter"]
        .sudo()
        .search([("key", "=", "account.show_line_subtotals_tax_selection")])
    )
    if tax_selection_param:
        if tax_selection_param.value == "business_relationship_dependent":
            tax_selection_param.value = "tax_excluded"
