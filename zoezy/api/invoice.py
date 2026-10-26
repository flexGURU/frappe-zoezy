from collections import defaultdict

import frappe
from frappe import _

from .utils import get_session_client, log_throw_error


@frappe.whitelist()
def get_invoices() -> list[dict]:
	client = get_session_client()
	if not client:
		return []

	try:
		invoices = frappe.get_all(
			"Client Invoice",
			filters={"client": client, "docstatus": 1},
			fields=[
				"name",
				"posting_date",
				"due_date",
				"status",
				"currency",
				"total",
				"outstanding_amount",
				"subscription",
			],
			order_by="posting_date desc, creation desc",
		)
		if not invoices:
			return []

		names = [invoice.name for invoice in invoices]
		packages = frappe.get_all(
			"Client Invoice Package",
			filters={"parent": ["in", names], "parenttype": "Client Invoice"},
			fields=["parent", "package_name", "unit_price"],
			order_by="idx asc",
		)
		payments = frappe.get_all(
			"Payment Entry",
			filters={"invoice": ["in", names], "docstatus": 1},
			fields=["name", "invoice", "amount", "posting_date", "mode_of_payment"],
			order_by="posting_date desc",
		)
	except Exception:
		log_throw_error(_("Error fetching invoices. Please try again."))

	packages_by_invoice = defaultdict(list)
	for package in packages:
		packages_by_invoice[package.parent].append(
			{"package_name": package.package_name, "unit_price": package.unit_price}
		)

	payments_by_invoice = defaultdict(list)
	for payment in payments:
		payments_by_invoice[payment.invoice].append(
			{
				"name": payment.name,
				"amount": payment.amount,
				"posting_date": str(payment.posting_date),
				"mode_of_payment": payment.mode_of_payment,
			}
		)

	return [
		{
			**invoice,
			"posting_date": str(invoice.posting_date),
			"due_date": str(invoice.due_date) if invoice.due_date else None,
			"packages": packages_by_invoice[invoice.name],
			"payments": payments_by_invoice[invoice.name],
		}
		for invoice in invoices
	]
