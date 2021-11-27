# -*- coding: utf-8 -*-

{
    "name": "B2B/B2C Business Relationship Types",
    "summary": """
        Manage business relationship types on contact level""",
    "description": """
        To facilitate different business realtionships, this adds configurable
        types, by default B2B, B2C and Internal.

        They can be used for automatic pricelist and fiscal positions assignment as
        well as contact specifc tax display settings.
    """,
    "author": "Michael Jurke, Ayudoo Ltd",
    "category": "Sales",
    "version": "0.1",
    "depends": [
        "base",
        "contacts",
        "product",
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/business_relationship_data.xml",
        "views/business_relationship_view.xml",
        "views/partner_view.xml",
        "views/account_move_view.xml",
        "views/pricelist_view.xml",
        "views/fiscal_position_view.xml",
        "views/templates.xml",
        "report/sale_report_view.xml",
    ],
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "post_init_hook": "init_partner_business_relationships",
    "uninstall_hook": "uninstall_hook",
}
