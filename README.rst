Business Relationship Types
===========================

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

**This module is in beta state. Feel free to provide feedback.**

Extend your contacts with business relationship types, e.g. `B2C`, `B2B` and
`Internal` and configure automatic assignment of pricelists and fiscal positions.
Change tax display (``Tax-Excluded (B2B)``, ``Tax-Included (B2C)``) of login users
according to the business relationship of the associated partner contact.

**Table of contents**

.. contents::
   :local:


Features
--------

Configurable business relationship types on contact level. Usable for

* automatic assignment of pricelists and fiscal positions
* different tax display settings for different users
* customize the default business relationship for new contacts
* assign a default image, salesperson or sales team to new contacts
* assign default salesperson and analytic account to sale orders
* restrict website menus, pages, redirects and block visibility to certain users
* use different access permission groups for portal users
* restrict product visibility to certain user groups
* create and configure your own business relationships
* individual pricelists for child contacts and sale order pricelists by shipping address


Typical use cases
-----------------

Different prices for user groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You want to offer different prices for customers like employees or agents? No problem,
just create the desired pricelist with a business relationship filter.


Business Relationship dependent Tax Display
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on your country's laws, you may have to show tax-included prices to B2C
customers, while you still want to show the lower tax-excluded prices for logged-in
B2B users.
By default, tax display is a global setting in Odoo. With this module you can
activate ``Business Relationship Dependent`` tax display and configure this option for
each business relationship separately.
The defaults are ``tax_excluded`` for `Internal` and `B2B`, but ``tax_included`` for
`B2C`.


Round prices for B2C
^^^^^^^^^^^^^^^^^^^^

Odoo manages tax-excluded and tax-included prices easily, but not both together.
Still, this may be your exact use case: You want to provide beautifully rounded
tax-included prices for your `B2C` customers, but correct tax-excluded prices for other
`B2B` transactions.

In `Manage prices for B2B (tax excluded) and B2C (tax
included) <https://www.odoo.com/documentation/14.0/applications/finance/accounting/taxation/taxes/B2B_B2C.html>`__
you find a detailed description of the problem and the documented workaround: While
basically working tax-excluded, you configure separate tax-included pricelists and
fiscal positions, that swap tax-excluded to tax-included. These have to be assigned
manually to your special tax-included customers and it won't work if this customer
has multiple delivery addresses that differ in tax handling (e.g. tax free export).

Here ``business_relationships`` comes to the help: instead of having to assign the
tax-included pricelists and fiscal position manually on each contact, you may use
automatic assignment based on the business relationships.


Pricelists according to shipping address
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tax included prices come with a drawback: your client might have a delivery address
in another country, that requires tax free export. The problem is, you cannot simply
remove the taxes with the default configuration, because tax free means 0% on the
invoice. To get things right, you will need to switch to a tax excluded pricelist,
easily done with this module by setting the two options
``individual pricelists for child contacts`` and
``sale order pricelist by shipping address``.


Usage
-----

Set your partner's business relationship in the contact form, right under the name. Out
of the box they can be used as additional filter option for your pricelists and fiscal
positions.


Automatic assignment
^^^^^^^^^^^^^^^^^^^^

Under ``Contacts`` -> ``Configuration`` -> ``Business Relationships`` you can modify
existing business relationships or create new ones. There is some basic configuration to
assign defaults to new contacts and on app installation, but they can be freely
reassigned.

There are `B2B`, `B2C` and `Internal`. `B2B` is default for
companies and for contacts, that have ``Purchase Payment Terms`` set (your
suppliers). `Internal` will be set for your employees (users of group
``base.group_user``). All further contacts are set to `B2C`. The match conditions
are configurable and the first matching business relationship will be assigned as
default to a new contact, if and only if you do not explicitly set another one.

If you need more options, don't hesitate to file a feature request.


Tax Display
^^^^^^^^^^^

If you want to adapt the ``Product Prices`` display, you need to set the option
under ``Settings`` -> ``Website`` -> ``Pricing`` to ``Business Relationship Dependent``.

Note, that ``tax_display`` depends on the currently logged-in user. Your website
customers will see prices according to this setting. However, in the admin backend
sale order and account move forms, the total/subtotal line display depends on the
setting for `Internal` users.


Email Template
~~~~~~~~~~~~~~

Odoo's sale order and move related email templates (not the attached reports)
display taxes according to the settings of the salesperson. If you want to
provide a consistent user experience, either create your own templates or assign a
salesperson to orders and invoices with the same setting as the targeted partner.

The recommended approach is to configure the `B2C` business relationship with a
salesperson with type `B2C`, e.g. `My B2C Shop`. In ``Contacts`` -> ``Configuration``
-> ``Business Relationships`` you can assign the default salesperson for new contacts
and update existing ones. For this to work in the website context, you need to check
`Enforce on sale orders in website context`.


Sales Order and Invoice PDF Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In difference to email templates, these are generated with the tax display settings of
the OdooBot. Depending on your requirements, you might want to create your own report
templates, that include conditions to display the right tax line values and contain
other business relationship dependent information. However, as an alternative or
support module, you may install the module ``salesperson_report_context``. Like emails,
the reports will be generated in the context of the associated salesperson and you can
rely on the salesperson configuration from above.
Please note, that this feature is still experimental.


Website User Types
------------------

As a website extension, you may install the auxiliary module ``Website User Types``.
After installation, login users will have an access permission group according to the
configuration of the business relationship of the contact, `Group B2C` and
`Group B2B`.


Pages, Menus and Redirects
^^^^^^^^^^^^^^^^^^^^^^^^^^

All three models can now be restricted to arbitrary Odoo access groups, including the
new ones from above. This way you can redirect your `B2B` (or other) customers to
specific landing pages, as well as restrict menu and page accessibility to different
user groups.


Block Visibility
^^^^^^^^^^^^^^^^

The web editor provides a new option ``Visibility``, that allows you to restrict the
visibility of any configurable block to `Group B2C`, `Group B2B` or a tax display
group. Use it, for example, to create business relationship dependent mega menu entries
or to add tax display specific information.

Note, these elements are simply hidden from the user, there is no additional server
rendering logic involved. For more sophisticated features you might rather consider
using a user group specific page or even a custom extension.


Product Accessibility
^^^^^^^^^^^^^^^^^^^^^

In the product form, `eCommerce` tab, you find the new section
`Website User Visibility`. Use it to remove product access of one of the user groups.

When unset, users of the group will not see the product in the shop list and accessing
the product page results in 404. However, internal users of group `Web Designer` are
still able to see and access it without limit.


Bug Tracker
-----------

Bugs are tracked on `GitHub Issues <https://github.com/ayudoo/odoo_business_relationships/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/ayudoo/odoo_business_relationships/issues/new?body=**Steps%20to%20reproduce**%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
-------

Authors
^^^^^^^

* Michael Jurke
* Ayudoo Ltd <support@ayudoo.bg>
