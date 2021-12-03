# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = ["res.partner"]
    _name = "res.partner"

    business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        string="Business Relationship",
        ondelete="restrict",
        tracking=True,
        help="The business relationship with this contact. Use for tax display,"
        + " fiscal positions and pricelists.",
    )

    @api.onchange(
        "is_company",
        "business_relationship_id",
        "property_supplier_payment_term_id",
    )
    def _compute_default_business_relationship_id(self):
        if not self.business_relationship_id:
            self.default_business_relationship_id = (
                self._get_default_business_relationship()
            )
        else:
            self.default_business_relationship_id = False

    # Used in the form to make the default transparent
    default_business_relationship_id = fields.Many2one(
        "res.partner.business_relationship",
        readonly=True,
        store=False,
        compute=_compute_default_business_relationship_id,
    )

    def _compute_same_as_parent_business_relationship_id(self):
        if self.business_relationship_id and self.parent_id:
            self.same_as_parent_business_relationship_id = (
                self.business_relationship_id == self.parent_id.business_relationship_id
            )
        else:
            self.same_as_parent_business_relationship_id = False

    same_as_parent_business_relationship_id = fields.Boolean(
        compute=_compute_same_as_parent_business_relationship_id,
    )

    child_contact_pricelist = fields.Selection(
        related="business_relationship_id.child_contact_pricelist",
        readonly=True,
    )

    def _after_business_relationship_changed(self):
        self._set_tax_groups()
        for child in self.child_ids:
            child.business_relationship_id = self.business_relationship_id

    def _set_tax_groups(self):
        tax_selection = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "account.show_line_subtotals_tax_selection", default="tax_excluded"
            )
        )
        if tax_selection != "business_relationship_dependent":
            return

        tax_excluded_group = self.env.ref(
            "account.group_show_line_subtotals_tax_excluded"
        )
        tax_included_group = self.env.ref(
            "account.group_show_line_subtotals_tax_included"
        )

        for record in self:
            if not record.business_relationship_id:
                continue

            tax_selection = (
                record.business_relationship_id.show_line_subtotals_tax_selection
            )
            if tax_selection == "tax_excluded":
                to_remove = tax_included_group
                to_add = tax_excluded_group
            else:
                to_remove = tax_excluded_group
                to_add = tax_included_group

            for user_id in record.with_context(active_test=False).user_ids.ids:
                self._cr.execute("""
                    DELETE FROM res_groups_users_rel
                    WHERE uid={} AND gid={}
                """.format(user_id, to_remove.id))

                to_remove.with_context(active_test=False).write(
                    {"users": [(3, user_id)]}
                )
                to_add.write({"users": [(4, user_id)]})

    @api.model
    def create(self, values):
        business_relationship_id = values.get("business_relationship_id", None)
        if business_relationship_id:
            business_relationship = self.env[
                "res.partner.business_relationship"
            ].browse(business_relationship_id)
        else:
            business_relationship = self._get_default_business_relationship(values)
        values["business_relationship_id"] = business_relationship.id

        for name, value in business_relationship.get_partner_default_values().items():
            if not values.get(name, None):
                values[name] = value

        r = super().create(values)
        r._after_business_relationship_changed()
        return r

    def write(self, values):
        old_business_relationship = None
        if "business_relationship_id" in values:
            old_business_relationship = self.business_relationship_id

        r = super().write(values)

        if (
            old_business_relationship is not None
            and old_business_relationship != self.business_relationship_id
        ):
            self._after_business_relationship_changed()

        return r

    # depends on business_relationship now, too
    @api.depends("country_id", "business_relationship_id")
    def _compute_product_pricelist(self):
        super()._compute_product_pricelist()

    def _get_default_business_relationship(self, values=None):
        if values is None:
            values = {}

        parent_id = values.get("parent_id", False)
        if parent_id:
            parent_id = self.env["res.partner"].browse(parent_id)
        else:
            parent_id = self.parent_id
        if parent_id and parent_id.business_relationship_id:
            return parent_id.business_relationship_id

        internal = False
        group_ids = self.env.context.get("user_group_ids", set())
        if group_ids:
            group_user_id = self.env.ref("base.group_user").id
            all_group_ids = set()
            for group_id in group_ids:
                all_group_ids.add(group_id)
                all_group_ids |= set(
                    self.env["res.groups"].browse(group_id).trans_implied_ids.ids
                )

            if group_user_id in all_group_ids:
                internal = True

        is_company = values.get("is_company", self.is_company)
        property_supplier_payment_term_id = values.get(
            "property_supplier_payment_term_id", self.property_supplier_payment_term_id
        )

        conditions = []
        fallback = [
            ("for_internal_users", "=", False),
            ("for_companies", "=", False),
            ("for_suppliers", "=", False),
        ]
        res = None
        if internal or is_company or property_supplier_payment_term_id:
            if internal:
                conditions.append(("for_internal_users", "=", True))
            if is_company:
                conditions.append(("for_companies", "=", True))
                if len(conditions) > 1:
                    conditions.insert(0, "|")
            if property_supplier_payment_term_id:
                conditions.append(("for_suppliers", "=", True))
                if len(conditions) > 1:
                    conditions.insert(0, "|")
            res = self.env["res.partner.business_relationship"].search(
                conditions, limit=1
            )

        if not res:
            res = self.env["res.partner.business_relationship"].search(
                fallback, limit=1
            )
            if not res:
                res = self.env["res.partner.business_relationship"].search([], limit=1)

        return res

    def _commercial_fields(self):
        # Remove pricelist from commercial fields if set to individual
        commercial_fields = super()._commercial_fields()
        if (
            self.child_contact_pricelist == "individual"
            and "property_product_pricelist" in commercial_fields
        ):
            commercial_fields.remove("property_product_pricelist")
        return commercial_fields

    @api.model
    def _init_partner_business_relationships(self):
        default = (
            self.env["res.partner.business_relationship"]
            .with_context(active_test=False)
            .search(
                [
                    ("for_suppliers", "=", False),
                    ("for_companies", "=", False),
                    ("for_internal_users", "=", False),
                ],
                limit=1,
            )
        )

        internal_users = (
            self.env["res.partner.business_relationship"].search(
                [("for_internal_users", "=", True)], limit=1
            )
            or default
        )
        companies = (
            self.env["res.partner.business_relationship"].search(
                [("for_companies", "=", True)], limit=1
            )
            or default
        )
        suppliers = (
            self.env["res.partner.business_relationship"].search(
                [("for_suppliers", "=", True)], limit=1
            )
            or default
        )

        child_partner_ids = (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search(
                [
                    ("business_relationship_id", "=", False),
                    ("parent_id", "!=", False),
                ]
            )
            .ids
        )

        for partner in (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search(
                [
                    ("business_relationship_id", "=", False),
                    ("parent_id", "=", False),
                ]
            )
        ):
            user_ids = partner.with_context(active_test=False).user_ids
            if user_ids and all(
                u.has_group("base.group_user") for u in user_ids
            ):
                partner.business_relationship_id = internal_users
            elif partner.is_company:
                partner.business_relationship_id = companies
            elif partner.property_supplier_payment_term_id:
                partner.business_relationship_id = suppliers
            else:
                partner.business_relationship_id = default

        # Set internal users regardless of parent partner configuration. This will
        # be the default case for the own company where the company itself has no
        # login.
        # Note, parent and child type will differ, which works, but will not be the
        # default usecase when you create contacts manually.
        for partner in self.env["res.partner"].browse(child_partner_ids):
            user_ids = partner.with_context(active_test=False).user_ids
            if user_ids and all(
                u.has_group("base.group_user") for u in user_ids
            ):
                partner.business_relationship_id = internal_users
