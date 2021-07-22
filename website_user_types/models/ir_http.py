# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _serve_redirect(cls):
        req_page = request.httprequest.path
        domain = [
            ("url_from", "=", req_page),
            ("|"),
            ("redirect_type", "in", ("301", "302")),
            ("redirect_type", "=", "403"),
            ("group_ids", "in", request.env.user.groups_id.ids),
        ]
        domain += request.website.website_domain()
        return request.env["website.rewrite"].sudo().search(domain, limit=1)
