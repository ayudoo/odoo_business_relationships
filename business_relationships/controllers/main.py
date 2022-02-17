# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleShipping(WebsiteSale):
    @http.route(
        ["/shop/confirm_order"], type="http", auth="public", website=True, sitemap=False
    )
    def confirm_order(self, **post):
        partner = request.env.user.partner_id
        if partner.business_relationship_id.sale_order_pricelist == "shipping":
            # Note, that the shipping addresses' pricelists have prevalence.
            # This means, that coupons and other geo filters for pricelists are ignored
            order = request.website.sale_get_order()

            if (
                order.partner_id != order.partner_shipping_id
                and order.partner_id.property_product_pricelist
                != order.partner_shipping_id.property_product_pricelist
            ):
                redirection = self.checkout_redirection(
                    order
                ) or self.checkout_check_address(order)
                if redirection:
                    return redirection

                order.onchange_partner_shipping_id()
                order.order_line._compute_tax_id()
                request.session["sale_last_order_id"] = order.id
                # force the pricelist from onchange_partner_shipping_id
                request.website.sale_get_order(
                    update_pricelist=True, force_pricelist=order.pricelist_id.id
                )
                extra_step = request.website.viewref("website_sale.extra_info_option")
                if extra_step.active:
                    return request.redirect("/shop/extra_info")

                return request.redirect("/shop/payment")

        return super().confirm_order(**post)
