# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleShipping(WebsiteSale):

    @http.route(
        ["/shop/confirm_order"], type="http", auth="public", website=True, sitemap=False
    )
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        partner = order.partner_id

        if partner.business_relationship_id.sale_order_pricelist == "shipping":
            # Note, that the shipping addresses' pricelists have prevalence.
            # This means, that coupons and other geo filters for pricelists are ignored
            if (
                order.pricelist_id
                != order.partner_shipping_id.property_product_pricelist
            ):
                redirection = self.checkout_redirection(
                    order
                ) or self.checkout_check_address(order)
                if redirection:
                    return redirection

                self._recompute_prices_after_shipping_change(order)
                request.session["sale_last_order_id"] = order.id

                extra_step = request.website.viewref("website_sale.extra_info_option")
                if extra_step.active:
                    return request.redirect("/shop/extra_info")

                return request.redirect("/shop/payment")

        return super().confirm_order(**post)

    def values_postprocess(self, order, mode, *args, **kwargs):
        new_values, errors, error_msg = super().values_postprocess(
            order, mode, *args, **kwargs
        )
        # so subclasses can customize
        if mode[0] in ('new', 'edit'):
            br = order.partner_id.business_relationship_id

            if br:
                if br.enforce_salesperson_website and br.salesperson_id:
                    # the salesperson was set on create
                    if order.user_id != br.salesperson_id:
                        new_values["user_id"] = br.salesperson_id.id
                    elif "user_id" in new_values:
                        del new_values["user_id"]

                if br.enforce_team_website and br.team_id:
                    if order.team_id != br.team_id:
                        new_values["team_id"] = br.team_id.id
                    elif "team_id" in new_values:
                        del new_values["team_id"]

        return new_values, errors, error_msg

    def checkout_values(self, **kw):
        order = request.website.sale_get_order()
        partner = order.partner_id

        if partner.business_relationship_id.sale_order_pricelist != "shipping":
            return super().checkout_values(**kw)

        shipping_before = order.partner_shipping_id
        values = super().checkout_values(**kw)
        order = values['order']

        if shipping_before != order.partner_shipping_id:
            self._recompute_prices_after_shipping_change(order)

        return values

    def _checkout_form_save(self, mode, checkout, all_values):
        partner_id = int(all_values.get('partner_id', 0))
        partner = request.env['res.partner'].browse(partner_id)
        order = request.website.sale_get_order()

        if not (
            order.partner_shipping_id == partner
            and mode[0] == 'edit'
            and partner.business_relationship_id.sale_order_pricelist == "shipping"
        ):
            return super()._checkout_form_save(mode, checkout, all_values)

        pricelist_before = partner.property_product_pricelist
        partner_id = super()._checkout_form_save(mode, checkout, all_values)

        if pricelist_before != partner.property_product_pricelist:
            self._recompute_prices_after_shipping_change(order)

        return partner_id

    def _recompute_prices_after_shipping_change(self, order):
        order.onchange_partner_shipping_id()
        order._compute_tax_id()
        request.website.sale_get_order(
            update_pricelist=True, force_pricelist=order.pricelist_id.id
        )
