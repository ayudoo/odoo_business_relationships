from odoo import api, fields, models


class BusinessRelationship(models.Model):
    _name = "res.partner.business_relationship"
    _inherit = ["image.mixin"]
    _description = "Business Relationship, e.g. B2B, B2C"
    _order = "sequence,id"

    sequence = fields.Integer("Sequence")

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
        translate=True,
    )

    def _compute_self_ref_ids(self):
        for record in self:
            record.self_ref_ids = record.ids

    self_ref_ids = fields.Many2many(
        "res.partner.business_relationship",
        compute=_compute_self_ref_ids,
    )

    color = fields.Integer(string="Color Index")

    active = fields.Boolean(
        default=True,
        help="If the active field is set to false, it will allow you to hide"
        + " Business Relationship without removing it.",
    )

    for_companies = fields.Boolean(
        string="Companies",
        default=False,
        help="triggers, if the contact is a company",
    )

    for_suppliers = fields.Boolean(
        string="Purchase (suppliers)",
        help="triggers, if purchase supplier payment terms are set",
        default=False,
    )

    for_internal_users = fields.Boolean(
        string="Internal Users",
        default=False,
        help="triggers, if the contact has an associated employee user login",
    )

    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
    )

    enforce_team_website = fields.Boolean(
        "Enforce team on sale orders in website context",
        default=False,
    )

    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
    )

    enforce_salesperson_website = fields.Boolean(
        "Enforce salesperson on sale orders in website context",
        default=False,
    )

    # TODO see https://github.com/odoo/odoo/commit/238a41e35280256382f6509182b9e900fb4f7aba#diff-695321b9df7129604a59fbc9bff34f97ba90b3394aa1166ca24e36b27389ae82
    # analytic_account_id = fields.Many2one(
    #     "account.analytic.account",
    #     string="Analytic Account",
    # )

    update_pricelist_by = fields.Selection(
        [
            ("partner", "Partner Address"),
            ("shipping", "Shipping Address"),
        ],
        string="Update Pricelist By",
        required=True,
        default="partner",
    )

    child_contact_pricelist = fields.Selection(
        [
            ("parent", "By Parent Contact"),
            ("individual", "Individual"),
        ],
        string="Child Contact Pricelist",
        required=True,
        default="parent",
    )

    partner_ids = fields.One2many(
        "res.partner",
        "business_relationship_id",
        string="Partners",
        context={"active_test": False},
    )

    def _compute_user_ids(self):
        for record in self:
            record.user_ids = record.partner_ids.with_context(
                active_test=False
            ).user_ids

    user_ids = fields.Many2many(
        "res.users",
        compute=_compute_user_ids,
        context={"active_test": False},
    )

    def get_partner_default_values(self):
        values = {}
        if self.image_1920:
            values["image_1920"] = self.image_1920

        # TODO how to provide this functionality in odoo 18
        # if self.team_id:
        #     values["team_id"] = self.team_id.id

        if self.salesperson_id:
            values["user_id"] = self.salesperson_id.id

        return values

    def get_sale_order_default_values(self, include_false=False):
        values = {}

        # TODO see https://github.com/odoo/odoo/commit/238a41e35280256382f6509182b9e900fb4f7aba#diff-695321b9df7129604a59fbc9bff34f97ba90b3394aa1166ca24e36b27389ae82
        # if self.analytic_account_id or include_false:
        #     values["analytic_account_id"] = self.analytic_account_id.id

        return values

    def open_invoicing_settings(self):
        """Utility method used to add an "Open Settings" button in views"""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "res.config.settings",
            "view_mode": "form",
            # 'res_id': self.commercial_partner_id.id,
            "target": "current",
            "flags": {"form": {"action_buttons": True}},
        }

    def action_assign_defaults_to_partners(self):
        for partner in self.partner_ids:
            for field_name, value in self.get_partner_default_values().items():
                # if not getattr(partner, field_name):
                # TODO add wizard, so users can choose whether to override existing
                # values
                setattr(partner, field_name, value)
