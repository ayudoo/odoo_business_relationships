from odoo import api, SUPERUSER_ID
from . import models, report


def init_partner_business_relationships(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner"]._init_partner_business_relationships()
