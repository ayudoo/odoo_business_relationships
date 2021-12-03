Salesperson Report Context
==========================

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

**This module is in beta state. Feel free to provide feedback.**

By default in Odoo, the tax line display of emails depends on the settings of the
salesperson, while reports - the attached PDF - will use the tax settings of the
OdooBot.

This very small module customizes report generation to use the salesperson settings.

It is kept separately for compatibility reasons and comes with a acceptable limitation:
you cannot select and print invoices of salespersons with different tax settings together.

If you create you own report templates, you may not need this.
