from odoo import api, SUPERUSER_ID
from . import controllers, models


def init_website_user_groups(env):
    env["res.partner.business_relationship"]._init_website_user_groups()
