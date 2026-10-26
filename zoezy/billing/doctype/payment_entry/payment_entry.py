# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PaymentEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		client: DF.Link | None
		client_name: DF.Data | None
		invoice: DF.Link
		mode_of_payment: DF.Literal["M-Pesa", "Cash", "Bank Transfer", "Card"]
		posting_date: DF.Datetime | None
		reference_no: DF.Data | None
	# end: auto-generated types

	def validate(self) -> None:
		self.validate_amount()

	def on_submit(self) -> None:
		self.get_invoice().apply_payment(self.amount)

	def on_cancel(self) -> None:
		self.get_invoice().apply_payment(-self.amount)

	def get_invoice(self):
		from zoezy.billing.doctype.client_invoice.client_invoice import ClientInvoice

		invoice: ClientInvoice = frappe.get_doc("Client Invoice", self.invoice)
		return invoice

	def validate_amount(self) -> None:
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero."))

		invoice = frappe.db.get_value(
			"Client Invoice", self.invoice, ["docstatus", "outstanding_amount"], as_dict=True
		)
		if invoice.docstatus != 1:
			frappe.throw(_("Invoice {0} must be submitted before it can be paid.").format(self.invoice))
		if flt(invoice.outstanding_amount) <= 0:
			frappe.throw(_("Invoice {0} is already fully paid.").format(self.invoice))
		if flt(self.amount) > flt(invoice.outstanding_amount):
			frappe.throw(
				_("Amount cannot exceed the outstanding amount of {0}.").format(invoice.outstanding_amount)
			)
