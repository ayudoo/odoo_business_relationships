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

        Property = self.env['ir.property'].with_company(company_id)
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook(company_id)

        # if no specific property, try to find a fitting pricelist
        specific_properties = Property._get_multi(
            'property_product_pricelist', Partner._name,
            list(models.origin_ids(partner_ids)),  # Some NewID can be in the partner_ids
        )
        result = {}
        remaining_partner_ids = []
        for pid in partner_ids:
            if (
                specific_properties.get(pid)
                and specific_properties[pid]._get_partner_pricelist_multi_filter_hook()
            ):
                result[pid] = specific_properties[pid]
            elif (
                isinstance(pid, models.NewId) and specific_properties.get(pid.origin)
                and specific_properties[pid.origin]._get_partner_pricelist_multi_filter_hook()
            ):
                result[pid] = specific_properties[pid.origin]
            else:
                remaining_partner_ids.append(pid)

        if remaining_partner_ids:
            # get fallback pricelist when no pricelist for a given country or business relationship
            pl_fallback = (
                Pricelist.search(
                    pl_domain
                    + [
                        ("country_group_ids", "=", False),
                        ("business_relationship_ids", "=", False),
                    ],
                    limit=1,
                )
                or Property._get("property_product_pricelist", "res.partner")
                or Pricelist.search(pl_domain, limit=1)
            )

            remaining_partners = self.env['res.partner'].browse(remaining_partner_ids)
            partners_by_br = remaining_partners.grouped('business_relationship_id')

            # group partners by country and business relationship,
            # and find a pricelist for each country + business relationship
            for business_relationship, br_partners in partners_by_br.items():
                for country, partners in br_partners.grouped("country_id").items():
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
