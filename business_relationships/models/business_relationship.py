# -*- coding: utf-8 -*-
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

    show_line_subtotals_tax_selection = fields.Selection(
        [
            ("tax_excluded", "Tax-Excluded"),
            ("tax_included", "Tax-Included"),
        ],
        string="Tax Display",
        required=True,
        default="tax_excluded",
    )

    salesteam_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
    )

    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
    )

    enforce_salesperson_website = fields.Boolean(
        "Enforce on sale orders in website context",
        default=False,
    )

    @api.onchange('show_line_subtotals_tax_selection', 'salesperson_id')
    def _compute_salesperson_tax_selection_matches(self):
        for record in self:
            if not record.salesperson_id:
                record.salesperson_tax_selection_matches = True
            else:
                s_tax_display = record.salesperson_id.partner_id.business_relationship_id.show_line_subtotals_tax_selection
                record.salesperson_tax_selection_matches = record.show_line_subtotals_tax_selection == s_tax_display

    salesperson_tax_selection_matches = fields.Boolean(
        string="Salesperson Tax Display Matches",
        compute=_compute_salesperson_tax_selection_matches,
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

    sale_order_pricelist = fields.Selection(
        [
            ("partner", "By Partner Address"),
            ("shipping", "By Shipping Address"),
        ],
        string="Sales Order Pricelist",
        required=True,
        default="partner",
    )

    partner_ids = fields.One2many(
        "res.partner",
        "business_relationship_id",
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

        if self.salesteam_id:
            values["salesteam_id"] = self.salesteam_id.id

        if self.salesperson_id:
            values["user_id"] = self.salesperson_id.id

        return values

    def write(self, values):
        old_tax_selection = self.show_line_subtotals_tax_selection
        super().write(values)

        if "show_line_subtotals_tax_selection" in values:
            if old_tax_selection != values["show_line_subtotals_tax_selection"]:
                self._update_users_tax_selection(
                    values["show_line_subtotals_tax_selection"]
                )

    def _update_users_tax_selection(self, new_value):
        if new_value == "tax_excluded":
            to_remove = self.env.ref("account.group_show_line_subtotals_tax_included")
            to_add = self.env.ref("account.group_show_line_subtotals_tax_excluded")
        else:
            to_remove = self.env.ref("account.group_show_line_subtotals_tax_excluded")
            to_add = self.env.ref("account.group_show_line_subtotals_tax_included")

        for user_id in self.partner_ids.with_context(active_test=False).user_ids.ids:
            # This is odd: adding works for inactive users, but removal not:
            # We need to remove it manually
            self._cr.execute("""
                DELETE FROM res_groups_users_rel
                WHERE uid={} AND gid={}
            """.format(user_id, to_remove.id))
            # and also from the cache:
            to_remove.write({"users": [(3, user_id)]})
            to_add.write({"users": [(4, user_id)]})

    def open_invoicing_settings(self):
        """ Utility method used to add an "Open Settings" button in views """
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
                if not getattr(partner, field_name):
                    setattr(partner, field_name, value)
