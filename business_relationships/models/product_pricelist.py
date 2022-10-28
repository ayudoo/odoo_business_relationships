from odoo import fields, models


class Pricelist(models.Model):
    _inherit = ["product.pricelist"]
    _name = "product.pricelist"

    business_relationship_ids = fields.Many2many(
        "res.partner.business_relationship",
        string="Business Relationships",
        help="Restrict automatic assignment to these business relationships.",
    )

    def _get_partner_pricelist_multi(self, partner_ids, company_id=None):
        """Retrieve the applicable pricelist for given partners in a given company.

        Extended, so it will return the pricelist of the partner business relationship
        accordingly.

        First, the pricelist of the specific property (res_id set), this one
               is created when saving a pricelist on the partner form view.
        Else, it will return the pricelist of the partner country group and
              business relationship
        Else, it will return the pricelist of either country group or business
              relationship, which one comes first, respectively
        Else, it will return the generic property (res_id not set), this one
              is created on the company creation.
        Else, it will return the first available pricelist

        :param company_id: if passed, used for looking up properties,
            instead of current user's company
        :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive uers. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env["res.partner"].with_context(active_test=False)
        company_id = company_id or self.env.company.id

        Property = self.env["ir.property"].with_company(company_id)
        Pricelist = self.env["product.pricelist"]
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook(company_id)

        # if no specific property, try to find a fitting pricelist
        result = Property._get_multi(
            "property_product_pricelist", Partner._name, partner_ids
        )

        remaining_partner_ids = [
            pid
            for pid, val in result.items()
            if not val or not val._get_partner_pricelist_multi_filter_hook()
        ]
        if remaining_partner_ids:
            # get fallback pricelist when no pricelist for a given country or business
            # relationship
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
            # group partners by country and business relationship,
            # and find a pricelist for each country + business relationship
            domain = [("id", "in", remaining_partner_ids)]
            groups = Partner.read_group(
                domain,
                ["business_relationship_id", "country_id"],
                ["business_relationship_id", "country_id"],
                lazy=False,
            )

            for group in groups:
                country_id = group["country_id"] and group["country_id"][0]
                business_relationship_id = (
                    group["business_relationship_id"]
                    and group["business_relationship_id"][0]
                )

                if country_id:
                    country_domain = ("country_group_ids.country_ids", "=", country_id)
                else:
                    country_domain = ("country_group_ids", "=", False)

                pl = Pricelist.search(
                    pl_domain
                    + [
                        country_domain,
                        ("|"),
                        ("business_relationship_ids", "=", business_relationship_id),
                        # match first business relationship indepent lists, too
                        ("business_relationship_ids", "=", False),
                    ],
                    limit=1,
                )

                if not pl and country_id:
                    # if not found by country, try a match by business relationship for
                    # country independent pricelists
                    pl = Pricelist.search(
                        pl_domain
                        + [
                            ("country_group_ids", "=", False),
                            (
                                "business_relationship_ids",
                                "=",
                                business_relationship_id,
                            ),
                        ],
                        limit=1,
                    )

                pl = pl or pl_fallback
                for pid in Partner.search(group["__domain"]).ids:
                    result[pid] = pl

        return result
