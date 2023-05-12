import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

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

    @api.depends("business_relationship_id")
    def _compute_can_change_business_relationship_id(self):
        for record in self:
            # For convenience, if a partner has an internal login, you can change it's
            # business relationship even if it has a parent_id. This is the typical
            # case for employees, being sub contacts of the company.

            ref = record
            if hasattr(ref, "_origin"):
                ref = ref._origin
            ref = ref.with_context(active_test=False)

            if ref.user_ids and any(
                user.has_group("base.group_user") for user in ref.user_ids
            ):
                record.can_change_business_relationship_id = True
            # on missmatch, it's editable so it can be fixed
            elif record.business_relationship_id and record.parent_id:
                record.can_change_business_relationship_id = (
                    record.business_relationship_id
                    != record.parent_id.business_relationship_id
                    or
                    # in Odoo 16, if it's not editable anymore it won't be saved
                    # so we need to chec ref, too.
                    ref.business_relationship_id
                    != record.parent_id.business_relationship_id
                )
            else:
                record.can_change_business_relationship_id = True

    can_change_business_relationship_id = fields.Boolean(
        compute=_compute_can_change_business_relationship_id,
    )

    child_contact_pricelist = fields.Selection(
        related="business_relationship_id.child_contact_pricelist",
        readonly=True,
    )

    @api.depends("country_id")
    @api.depends_context("company")
    def _compute_is_fixed_property_pricelist(self):
        for record in self:
            actual = self.env["ir.property"]._get(
                "property_product_pricelist",
                "res.partner",
                "res.partner,%s" % record.id,
            )
            if actual:
                record.is_fixed_property_pricelist = True
            else:
                record.is_fixed_property_pricelist = False

    def _search_is_fixed_property_pricelist(self, operator, operand):
        if operator != "=":
            raise UserError("Property Pricelist search only works with operator '='.")

        if operand is True:
            operator = "in"
        elif operand is False:
            operator = "not in"
        else:
            raise UserError(
                "Property Pricelist search only works operands True and False."
            )

        domain = self.env["ir.property"]._get_domain(
            "property_product_pricelist", "res.partner"
        )
        properties = self.env["ir.property"].search(domain)
        res_ids = [int(p["res_id"].split(",")[1]) for p in properties.read(["res_id"])]
        return [("id", "in", res_ids)]

    is_fixed_property_pricelist = fields.Boolean(
        "Pricelist is fixed on this contact",
        compute=_compute_is_fixed_property_pricelist,
        search=_search_is_fixed_property_pricelist,
    )

    def reset_fixed_property_pricelist(self):
        self.env["ir.property"]._set_multi(
            "property_product_pricelist",
            self._name,
            {self.id: False},
        )

    def make_property_pricelist_fixed(self):
        self.env["ir.property"]._set_multi(
            "property_product_pricelist",
            self._name,
            {self.id: self.property_product_pricelist},
        )

    def _after_business_relationship_changed(self):
        self.ensure_one()
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
                self._cr.execute(
                    """
                    DELETE FROM res_groups_users_rel
                    WHERE uid={} AND gid={}
                """.format(
                        user_id, to_remove.id
                    )
                )

                to_remove.with_context(active_test=False).write(
                    {"users": [(3, user_id)]}
                )
                to_add.write({"users": [(4, user_id)]})

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            self._set_default_business_relationship_values(values)

        partners = super().create(values_list)

        for partner in partners:
            partner._after_business_relationship_changed()

        return partners

    def _set_default_business_relationship_values(self, values):
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

        internal = self.env.context.get("business_relationship_internal_user", False)
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
            if user_ids and all(u.has_group("base.group_user") for u in user_ids):
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
            if user_ids and all(u.has_group("base.group_user") for u in user_ids):
                partner.business_relationship_id = internal_users
