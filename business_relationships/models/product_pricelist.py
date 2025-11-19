from odoo import api, fields, models


class Pricelist(models.Model):
    _inherit = ["product.pricelist"]
    _name = "product.pricelist"

    business_relationship_ids = fields.Many2many(
        "res.partner.business_relationship",
        string="Business Relationships",
        help="Restrict automatic assignment to these business relationships.",
    )

    @api.model
    def _get_partner_pricelist_multi(self, partner_ids):
        """ Retrieve the applicable pricelist for given partners in a given company.

        It will return the first found pricelist in this order:
        First, the pricelist of the specific property (res_id set), this one
                is created when saving a pricelist on the partner form view.
        Else, it will return the pricelist of the partner country group
        Else, it will return the generic property (res_id not set)
        Else, it will return the first available pricelist if any

        :param int company_id: if passed, used for looking up properties,
            instead of current user's company
        :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive users. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        company_id = self.env.company.id

        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook(company_id)

        # if no specific property, try to find a fitting pricelist
        result = {}
        remaining_partner_ids = []
        for partner in Partner.browse(partner_ids):
            if partner.specific_property_product_pricelist._get_partner_pricelist_multi_filter_hook():
                result[partner.id] = partner.specific_property_product_pricelist
            else:
                remaining_partner_ids.append(partner.id)

        if remaining_partner_ids:
            def convert_to_int(string_value):
                try:
                    return int(string_value)
                except (TypeError, ValueError, OverflowError):
                    return None

            # get fallback pricelist when no pricelist for a given country or business relationship
            pl_fallback = (
                Pricelist.search(
                    pl_domain
                    + [
                        ("country_group_ids", "=", False),
                        ("business_relationship_ids", "=", False),
                    ],
                    limit=1,
                ) or
                Pricelist.browse(convert_to_int(IrConfigParameter.get_param(f'res.partner.property_product_pricelist_{company_id}'))) or
                Pricelist.browse(convert_to_int(IrConfigParameter.get_param('res.partner.property_product_pricelist'))) or
                Pricelist.search(pl_domain, limit=1)
            )

            remaining_partners = self.env['res.partner'].browse(remaining_partner_ids)
            partners_by_br = remaining_partners.grouped('business_relationship_id')

            # group partners by country and business relationship,
            # and find a pricelist for each country + business relationship
            for business_relationship, br_partners in partners_by_br.items():
                for country, partners in br_partners.grouped("country_id").items():
                    if not country and (country_code := self.env.context.get('country_code')):
                        country = self.env['res.country'].search([('code', '=', country_code)], limit=1)

                    if country:
                        country_domain = ("country_group_ids.country_ids", "=", country.id)
                    else:
                        country_domain = ("country_group_ids", "=", False)

                    pl = Pricelist.search(
                        pl_domain
                        + [
                            country_domain,
                            ("|"),
                            ("business_relationship_ids", "=", business_relationship.id),
                            # match first business relationship indepent lists, too
                            ("business_relationship_ids", "=", False),
                        ],
                        limit=1,
                    )

                    if not pl and country:
                        # if not found by country, try a match by business relationship for
                        # country independent pricelists
                        pl = Pricelist.search(
                            pl_domain
                            + [
                                ("country_group_ids", "=", False),
                                (
                                    "business_relationship_ids",
                                    "=",
                                    business_relationship.id,
                                ),
                            ],
                            limit=1,
                        )
                    pl = pl or pl_fallback
                    result.update(dict.fromkeys(partners._ids, pl))

        return result
