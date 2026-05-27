# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClientInvoicePackage(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        package_name: DF.Link
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        unit_price: DF.Float
    # end: auto-generated types

    pass
