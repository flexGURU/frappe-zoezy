# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

DEFAULT_LOGO = "/assets/zoezy/icons/desktop_icons/zoezy.svg"


class ZoezySettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active_period_duration: DF.Int
		allow_client_signup: DF.Check
		app_logo: DF.AttachImage | None
		brand_name: DF.Data | None
		default_currency: DF.Link | None
		invoice_due_days: DF.Int
		payment_number: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.make_logo_public()

	def make_logo_public(self):
		if not (self.app_logo or "").startswith("/private/"):
			return

		file_name = frappe.db.get_value("File", {"file_url": self.app_logo})
		if not file_name:
			return

		file = frappe.get_doc("File", file_name)
		file.is_private = 0
		file.save(ignore_permissions=True)
		self.app_logo = file.file_url


def get_branding() -> dict:
	settings = frappe.get_cached_doc("Zoezy Settings")
	return {
		"brand_name": settings.brand_name or "Zoezy",
		"logo": settings.app_logo or None,
		"allow_signup": bool(settings.allow_client_signup),
		"default_logo": DEFAULT_LOGO,
	}


def get_settings() -> dict:
	settings = frappe.get_cached_doc("Zoezy Settings")
	return {
		**get_branding(),
		"currency": settings.default_currency or frappe.db.get_default("currency") or "KES",
		"payment_number": settings.payment_number,
	}
