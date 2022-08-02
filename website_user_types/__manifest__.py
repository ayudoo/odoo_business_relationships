# -*- coding: utf-8 -*-

{
    "author": "Michael Jurke, Ayudoo EOOD",
    "name": "Website User Types",
    "version": "0.1",
    "summary": """
        Extends business relationships with website access permission groups
        """,
    "description": """
        Based on the powerfull business relationships module, you can now configure
        menus, pages, redirects and block visibility by website user type access groups
        accoring to the business relationship with the contact.
    """,
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "depends": [
        "base",
        "website",
        "website_sale",
        "business_relationships",
    ],
    "data": [
        "security/website_user_type_security.xml",
        "security/website_security.xml",
        "data/business_relationship_data.xml",
        "views/business_relationship_view.xml",
        "views/product_template_view.xml",
        "views/website_menu_view.xml",
        "views/website_rewrite_view.xml",
        "views/website_page_view.xml",
        "views/snippets/snippets.xml",
        "views/templates/layout.xml",
    ],
    "assets": {
        'web.assets_frontend': [
            "website_user_types/static/src/scss/frontend.scss",
        ],
    },
    "license": "LGPL-3",
    "post_init_hook": "init_website_user_groups",
    "demo": [],
}
