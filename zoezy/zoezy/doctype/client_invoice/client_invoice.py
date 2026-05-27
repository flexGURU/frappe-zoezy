# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClientInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from zoezy.zoezy.doctype.client_invoice_package.client_invoice_package import ClientInvoicePackage

		amended_from: DF.Link | None
		client: DF.Link
		client_name: DF.Data | None
		packages: DF.Table[ClientInvoicePackage]
		posting_date: DF.Date
		status: DF.Literal["Paid", "Overdue", "Unpaid"]
		subscription: DF.Link | None
		total: DF.Float
	# end: auto-generated types

	pass
