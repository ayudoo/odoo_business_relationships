# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from . import models


def init_website_user_groups(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.partner.business_relationship"]._init_website_user_groups()
