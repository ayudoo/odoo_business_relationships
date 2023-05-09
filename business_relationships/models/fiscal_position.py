from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _name = "account.fiscal.position"
    _inherit = "account.fiscal.position"

    business_relationship_ids = fields.Many2many(
        "res.partner.business_relationship",
        string="Business Relationships",
        help="Restrict automatic assignment to these business relationships.",
    )

    # extend auto_apply functionality
    @api.model
    def _get_fpos_by_region(
        self,
        country_id=False,
        state_id=False,
        zipcode=False,
        vat_required=False,
        business_relationship=None,
    ):
        if not country_id:
            return False
        base_domain = [
            ("auto_apply", "=", True),
            ("vat_required", "=", vat_required),
            ("company_id", "in", [self.env.company.id, False]),
        ]

        # if no business_relationship is given, use the one of the public user
        if not business_relationship:
            public_user = self.env.ref('base.public_user')
            business_relationship = public_user.business_relationship_id

        # add business relationship domain
        if business_relationship:
            base_domain += [
                ("|"),
                ("business_relationship_ids", "=", business_relationship.id),
                ("business_relationship_ids", "=", False),
            ]

        null_state_dom = state_domain = [("state_ids", "=", False)]
        null_zip_dom = zip_domain = [("zip_from", "=", False), ("zip_to", "=", False)]
        null_country_dom = [
            ("country_id", "=", False),
            ("country_group_id", "=", False),
        ]

        if zipcode:
            zip_domain = [("zip_from", "<=", zipcode), ("zip_to", ">=", zipcode)]

        if state_id:
            state_domain = [("state_ids", "=", state_id)]

        domain_country = base_domain + [("country_id", "=", country_id)]
        domain_group = base_domain + [("country_group_id.country_ids", "=", country_id)]

        # Build domain to search records with exact matching criteria
        fpos = self.search(domain_country + state_domain + zip_domain, limit=1)
        # return records that fit the most the criteria, and fallback on less specific
        # fiscal positions if any can be found
        if not fpos and state_id:
            fpos = self.search(domain_country + null_state_dom + zip_domain, limit=1)
        if not fpos and zipcode:
            fpos = self.search(domain_country + state_domain + null_zip_dom, limit=1)
        if not fpos and state_id and zipcode:
            fpos = self.search(domain_country + null_state_dom + null_zip_dom, limit=1)

        # fallback: country group with no state/zip range
        if not fpos:
            fpos = self.search(domain_group + null_state_dom + null_zip_dom, limit=1)

        if not fpos:
            # Fallback on catchall (no country, no group)
            fpos = self.search(base_domain + null_country_dom, limit=1)
        return fpos

    @api.model
    def _get_fiscal_position(self, partner, delivery=None):
        """
        :return: fiscal position found (recordset)
        :rtype: :class:`account.fiscal.position`
        """
        if not partner:
            return self.env["account.fiscal.position"]

        if not delivery:
            delivery = partner

        # partner manually set fiscal position always win
        if (
            delivery.property_account_position_id
            or partner.property_account_position_id
        ):
            return (
                delivery.property_account_position_id
                or partner.property_account_position_id
            )

        # First search only matching VAT positions
        vat_required = bool(partner.vat)
        fp = self._get_fpos_by_region(
            delivery.country_id.id,
            delivery.state_id.id,
            delivery.zip,
            vat_required,
            business_relationship=partner.business_relationship_id,
        )

        # Then if VAT required found no match, try positions that do not require it
        if not fp and vat_required:
            fp = self._get_fpos_by_region(
                delivery.country_id.id,
                delivery.state_id.id,
                delivery.zip,
                False,
                business_relationship=partner.business_relationship_id,
            )

        return fp or self.env["account.fiscal.position"]
