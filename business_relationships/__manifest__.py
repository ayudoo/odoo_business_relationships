# -*- coding: utf-8 -*-

{
    "author": "Michael Jurke, Ayudoo Ltd",
    "name": "B2B/B2C Business Relationship Types",
    "version": "0.1",
    "summary": "Manage business relationship types on contact level",
    "description": """
        To facilitate different business realtionships, this adds configurable
        types, by default B2B, B2C and Internal.

        They can be used for automatic pricelist and fiscal positions assignment as
        well as contact specifc tax display settings.
    """,
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "support": "support@ayudoo.bg",
    "depends": [
        "base",
        "contacts",
        # product dependency comes with sale -> payment -> account
        # "product",
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
        "report/sale_report_view.xml",
    ],
    "assets": {
        'web.assets_backend': [
            "business_relationships/static/src/scss/backend.scss",
        ],
    },
    "application": True,
    "installable": True,
    "post_init_hook": "init_partner_business_relationships",
    "uninstall_hook": "uninstall_hook",
}
