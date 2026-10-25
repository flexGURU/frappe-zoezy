import frappe
from frappe.utils import add_days, flt

from zoezy.billing.doctype.client_invoice.client_invoice import get_invoice_status
from zoezy.clients.doctype.client.client import update_client_status
from zoezy.clients.doctype.client_subscription.client_subscription import get_subscription_status
from zoezy.zoezy.doctype.zoezy_settings.zoezy_settings import get_settings


def execute():
	if not frappe.db.exists("Singles", {"doctype": "Zoezy Settings", "field": "invoice_due_days"}):
		frappe.db.set_single_value("Zoezy Settings", "invoice_due_days", 7)
	recompute_final_weights()
	backfill_invoices()
	refresh_statuses()


def recompute_final_weights():
	rows = frappe.get_all(
		"Workout Log Exercise",
		filters={"progressive_overload": 1},
		fields=["name", "sets", "start_weight", "progression_weight"],
	)
	for row in rows:
		final_weight = flt(row.start_weight + row.progression_weight * max(row.sets - 1, 0), 2)
		frappe.db.set_value("Workout Log Exercise", row.name, "final_weight", final_weight)


def backfill_invoices():
	due_days = frappe.db.get_single_value("Zoezy Settings", "invoice_due_days") or 7
	currency = get_settings()["currency"]
	invoices = frappe.get_all(
		"Client Invoice",
		fields=["name", "docstatus", "posting_date", "due_date", "currency", "total", "outstanding_amount"],
	)
	for invoice in invoices:
		due_date = invoice.due_date or add_days(invoice.posting_date, due_days)
		frappe.db.set_value(
			"Client Invoice",
			invoice.name,
			{
				"due_date": due_date,
				"currency": invoice.currency or currency,
				"status": get_invoice_status(
					invoice.docstatus, invoice.total, invoice.outstanding_amount, due_date
				),
			},
			update_modified=False,
		)


def refresh_statuses():
	for subscription in frappe.get_all("Client Subscription", fields=["name", "from_date", "to_date"]):
		frappe.db.set_value(
			"Client Subscription",
			subscription.name,
			"status",
			get_subscription_status(subscription.from_date, subscription.to_date),
			update_modified=False,
		)

	for client in frappe.get_all("Client", pluck="name"):
		update_client_status(client)
