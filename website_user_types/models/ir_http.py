# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _serve_redirect(cls):
        req_page = request.httprequest.path
        domain = [
            "|",
            ('url_from', '=', req_page.rstrip('/')),
            ('url_from', '=', req_page + '/'),
            "|",
            ("redirect_type", "in", ("301", "302")),
            "&",
            ("redirect_type", "=", "403"),
            ("group_ids", "in", request.env.user.groups_id.ids),
        ]
        domain += request.website.with_context(with_group_ids=False).website_domain()
        return request.env["website.rewrite"].sudo().search(domain, limit=1)

    @classmethod
    def _serve_page(cls):
        # this might have side effect in unknown extension, but this way we do not
        # need to fully override _serve_page with potatially more clashes
        request.website = request.website.with_context(
            with_group_ids=request.env.user.groups_id.ids
        )
        return super()._serve_page()
