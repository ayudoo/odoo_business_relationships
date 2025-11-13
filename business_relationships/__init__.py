from odoo import api, SUPERUSER_ID
from . import models, report


def init_partner_business_relationships(env):
    env["res.partner"]._init_partner_business_relationships()
