# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, getdate, today

from zoezy.zoezy.doctype.zoezy_settings.zoezy_settings import get_settings


class ClientInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from zoezy.billing.doctype.client_invoice_package.client_invoice_package import ClientInvoicePackage

		amended_from: DF.Link | None
		client: DF.Link
		client_name: DF.Data | None
		currency: DF.Link | None
		due_date: DF.Date | None
		outstanding_amount: DF.Currency
		packages: DF.Table[ClientInvoicePackage]
		posting_date: DF.Date
		status: DF.Literal["", "Unpaid", "Partially Paid", "Paid", "Overdue", "Cancelled"]
		subscription: DF.Link
		total: DF.Currency
	# end: auto-generated types

	def validate(self) -> None:
		self.validate_subscription()
		self.set_defaults()
		self.set_total()
		self.outstanding_amount = self.total
		self.set_status()

	def on_submit(self) -> None:
		self.send_email_notification()

	def on_cancel(self) -> None:
		self.db_set("status", "Cancelled")

	def validate_subscription(self) -> None:
		subscription_client = frappe.db.get_value("Client Subscription", self.subscription, "client")
		if subscription_client != self.client:
			frappe.throw(_("Subscription {0} does not belong to {1}.").format(self.subscription, self.client))

	def set_defaults(self) -> None:
		if not self.currency:
			self.currency = get_settings()["currency"]
		if not self.due_date:
			due_days = frappe.db.get_single_value("Zoezy Settings", "invoice_due_days") or 0
			self.due_date = add_days(self.posting_date, due_days)
		if getdate(self.due_date) < getdate(self.posting_date):
			frappe.throw(_("Due Date cannot be before the Posting Date."))

	def set_total(self) -> None:
		for row in self.packages:
			if flt(row.unit_price) < 0:
				frappe.throw(_("Row {0}: Unit Price cannot be negative.").format(row.idx))
		self.total = flt(sum(flt(row.unit_price) for row in self.packages), 2)

	def set_status(self) -> None:
		self.status = get_invoice_status(self.docstatus, self.total, self.outstanding_amount, self.due_date)

	def apply_payment(self, amount: float) -> None:
		outstanding = flt(self.outstanding_amount - amount, 2)
		if outstanding < 0:
			frappe.throw(
				_("Payment exceeds the outstanding amount of {0} on {1}.").format(
					self.outstanding_amount, self.name
				)
			)
		if outstanding > self.total:
			frappe.throw(_("Outstanding amount on {0} cannot exceed its total.").format(self.name))

		self.outstanding_amount = outstanding
		self.set_status()
		self.db_set(
			{"outstanding_amount": self.outstanding_amount, "status": self.status},
			notify=True,
		)

	def send_email_notification(self) -> None:
		if self.status not in ("Unpaid", "Overdue") or not self.client:
			return

		settings = get_settings()
		email_args = self.as_dict()
		email_args["brand"] = settings["brand_name"]
		try:
			frappe.sendmail(
				recipients=[self.client],
				subject=f"Invoice {self.name} from {settings['brand_name']}",
				template="invoice",
				args=email_args,
				reference_doctype=self.doctype,
				reference_name=self.name,
			)
		except frappe.OutgoingEmailError:
			frappe.log_error(title=f"Could not email invoice {self.name}")


def get_invoice_status(docstatus: int, total: float, outstanding: float, due_date) -> str:
	if docstatus == 2:
		return "Cancelled"
	if flt(outstanding) <= 0:
		return "Paid"
	if due_date and getdate(due_date) < getdate(today()):
		return "Overdue"
	if flt(outstanding) < flt(total):
		return "Partially Paid"
	return "Unpaid"


def mark_overdue_invoices() -> None:
	overdue = frappe.get_all(
		"Client Invoice",
		filters={
			"docstatus": 1,
			"status": ["in", ["Unpaid", "Partially Paid"]],
			"due_date": ["<", today()],
			"outstanding_amount": [">", 0],
		},
		pluck="name",
	)
	for name in overdue:
		frappe.db.set_value("Client Invoice", name, "status", "Overdue")
