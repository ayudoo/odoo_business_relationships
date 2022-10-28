from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    # Note, we don't need to override _serve_redirect as it is only called in
    # _serve_page, and website_domain will contain the group filter
    # @classmethod
    # def _serve_redirect(cls):

    @classmethod
    def _serve_page(cls):
        # this might have side effect in unknown extension, but this way we do not
        # need to fully override _serve_page with potatially more clashes
        request.website = request.website.with_context(
            with_group_ids=request.env.user.groups_id.ids
        )
        return super()._serve_page()
