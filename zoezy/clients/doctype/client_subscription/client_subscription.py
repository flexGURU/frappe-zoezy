# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today

from zoezy.clients.doctype.client.client import update_client_status


class ClientSubscription(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		client: DF.Link
		from_date: DF.Date
		package_price: DF.Currency
		package_type: DF.Link
		status: DF.Literal["Active", "Upcoming", "Expired"]
		to_date: DF.Date
	# end: auto-generated types

	def before_validate(self) -> None:
		if self.from_date and not self.to_date:
			self.to_date = self.add_days_to_date()

	def validate(self) -> None:
		self.validate_dates()
		self.validate_overlap()
		self.status = get_subscription_status(self.from_date, self.to_date)

	def after_insert(self) -> None:
		self.create_invoice()

	def on_update(self) -> None:
		update_client_status(self.client)

	def after_delete(self) -> None:
		update_client_status(self.client)

	def validate_dates(self) -> None:
		if self.from_date and self.to_date and getdate(self.to_date) < getdate(self.from_date):
			frappe.throw(_("To Date cannot be before From Date."))

	def validate_overlap(self) -> None:
		overlapping = frappe.db.get_value(
			"Client Subscription",
			{
				"client": self.client,
				"package_type": self.package_type,
				"name": ["!=", self.name],
				"from_date": ["<=", self.to_date],
				"to_date": [">=", self.from_date],
			},
			"name",
		)
		if overlapping:
			frappe.throw(
				_("This client already has a {0} subscription ({1}) covering these dates.").format(
					self.package_type, overlapping
				)
			)

	@frappe.whitelist()
	def add_days_to_date(self) -> str | None:
		duration = frappe.db.get_single_value("Zoezy Settings", "active_period_duration") or 30
		if self.from_date:
			return add_days(self.from_date, duration)

	def create_invoice(self) -> None:
		invoice = frappe.new_doc("Client Invoice")
		invoice.client = self.client
		invoice.subscription = self.name
		invoice.posting_date = self.from_date
		invoice.append(
			"packages",
			{"package_name": self.package_type, "unit_price": self.package_price},
		)
		invoice.insert(ignore_permissions=True)
		invoice.submit()


def get_subscription_status(from_date, to_date) -> str:
	now = getdate(today())
	if getdate(to_date) < now:
		return "Expired"
	if getdate(from_date) > now:
		return "Upcoming"
	return "Active"


def update_subscription_statuses() -> None:
	subscriptions = frappe.get_all(
		"Client Subscription",
		filters={"status": ["in", ["Active", "Upcoming"]]},
		fields=["name", "client", "from_date", "to_date", "status"],
	)

	for subscription in subscriptions:
		status = get_subscription_status(subscription.from_date, subscription.to_date)
		if status == subscription.status:
			continue

		try:
			frappe.db.set_value("Client Subscription", subscription.name, "status", status)
			update_client_status(subscription.client)
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			frappe.log_error(
				title=f"Error updating status of subscription {subscription.name}",
				message=frappe.get_traceback(),
			)
