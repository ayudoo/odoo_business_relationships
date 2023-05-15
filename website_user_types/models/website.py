from odoo import api, models, tools
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_available_website_user_group_ids(self):
        return [
            self.env.ref("base.group_user").id,
            self.env.ref("website_user_types.group_b2c").id,
            self.env.ref("website_user_types.group_b2b").id,
            self.env.ref("base.group_public").id,
        ]

    def get_website_user_group_cache_key(self):
        user_group_ids = self.env.user.groups_id.ids
        for group_id in self.get_available_website_user_group_ids():
            if group_id in user_group_ids:
                return f"website_user_types_group_{group_id}"

        return "website_user_types_group_{}".format(
            self.env.ref("base.group_public").id
        )

    @tools.ormcache('self.env.uid')
    def get_website_user_group_classes(self):
        if self.user_has_groups("account.group_show_line_subtotals_tax_included"):
            wut_class = "wut_tax_included"
        else:
            wut_class = "wut_tax_excluded"

        if self.user_has_groups("website_user_types.group_b2b"):
            return "{} wut_group_b2b".format(wut_class)
        if self.user_has_groups("website_user_types.group_b2c"):
            return "{} wut_group_b2c".format(wut_class)
        return wut_class

    def sale_get_order(
        self,
        force_create=False,
        update_pricelist=False,
    ):
        sale_order = super().sale_get_order(
            force_create=force_create, update_pricelist=update_pricelist
        )
        if update_pricelist or force_create:
            partner = sale_order.partner_id
            if partner.business_relationship_id.update_prices:
                pricelist = self._get_default_business_relationship_pricelist(
                    sale_order
                )
                fiscal_position = self.env[
                    'account.fiscal.position'
                ].sudo()._get_fiscal_position(partner, sale_order.partner_shipping_id)

                if (
                    pricelist != sale_order.pricelist_id
                    or fiscal_position != sale_order.fiscal_position_id
                ):
                    if pricelist != sale_order.pricelist_id:
                        request.session['website_sale_current_pl'] = pricelist.id

                    sale_order.write({
                        'pricelist_id': pricelist.id,
                        'fiscal_position_id': fiscal_position.id,
                    })
                    sale_order._recompute_prices()

        return sale_order

    def _get_default_business_relationship_pricelist(self, order):
        partner = order.partner_id

        if partner.business_relationship_id.update_pricelist_by == "shipping":
            partner = order.partner_shipping_id

        return partner.property_product_pricelist

    @api.model
    def website_domain(self, website_id=False):
        # there is no perfect solution, either fully override _serve_page, or
        # use with_group_ids context for website but not view to keep compatibility high
        domain = super().website_domain(website_id=website_id)
        group_ids = self.env.context.get("with_group_ids", False)
        if group_ids:
            domain = domain + [
                ("|"),
                ("group_ids", "=", False),
                ("group_ids", "in", group_ids),
            ]

        return domain

    def sale_product_domain(self):
        domain = super().sale_product_domain()

        if self.user_has_groups("website.group_website_designer"):
            return domain

        # A user having both groups cannot be configured with business relationships,
        # but you can do so in the technical admin user settings
        if self.user_has_groups(
            "website_user_types.group_b2b"
        ) and self.user_has_groups("website_user_types.group_b2c"):
            domain = domain + [
                ("|"),
                ("visible_group_b2c", "=", True),
                ("visible_group_b2b", "=", True),
            ]
        else:
            if self.user_has_groups("website_user_types.group_b2b"):
                domain.append(
                    ("visible_group_b2b", "=", True),
                )
            else:
                domain.append(
                    ("visible_group_b2c", "=", True),
                )

        return domain


class View(models.Model):
    _inherit = "ir.ui.view"
    _name = "ir.ui.view"

    @api.model
    @tools.ormcache_context(
        "self.env.uid", "self.env.su", "xml_id", keys=("website_id",)
    )
    def get_view_id(self, xml_id):
        self = self.with_context(with_group_ids=False)
        return super().get_view_id(xml_id)

    @api.model
    def _get_inheriting_views_arch_domain(self, model):
        self = self.with_context(with_group_ids=False)
        return super()._get_inheriting_views_arch_domain(model)
