# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Client(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age: DF.Int
		date_joined: DF.Date | None
		email: DF.Link
		first_name: DF.Data | None
		full_name: DF.Data | None
		last_name: DF.Data | None
		lead_source: DF.Link | None
		phone_number: DF.Data | None
		profile_image: DF.AttachImage | None
		status: DF.Literal["Active", "Inactive"]
		userid: DF.Link | None
	# end: auto-generated types

	def validate(self):
		self.set_full_name()
		self.userid = self.email
		self.status = get_client_status(self.name or self.email)

	def after_insert(self):
		setup_client_user(self.email)

	def set_full_name(self):
		self.full_name = " ".join(part for part in (self.first_name, self.last_name) if part) or self.email


def setup_client_user(user: str) -> None:
	if "Client" not in frappe.get_roles(user):
		user_doc = frappe.get_doc("User", user)
		user_doc.flags.ignore_permissions = True
		user_doc.add_roles("Client")
	if not frappe.db.get_value("User", user, "default_app"):
		frappe.db.set_value("User", user, "default_app", "zoezy")


def get_client_status(client: str) -> str:
	has_active_subscription = frappe.db.exists("Client Subscription", {"client": client, "status": "Active"})
	return "Active" if has_active_subscription else "Inactive"


def update_client_status(client: str) -> None:
	status = get_client_status(client)
	if frappe.db.get_value("Client", client, "status") != status:
		frappe.db.set_value("Client", client, "status", status, update_modified=False)
