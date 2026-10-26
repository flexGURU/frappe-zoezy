import re

import frappe
from frappe import _
from frappe.core.doctype.user.user import User
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address

from .utils import log_throw_error

PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9 ]{6,15}$")
MAX_NAME_LENGTH = 60


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=3600)
@rate_limit(key="email", limit=5, seconds=1800)
def sign_up(first_name: str, last_name: str, email: str, phone: str) -> None:
	if not signup_allowed():
		frappe.throw(_("Sign up is disabled. Please contact your trainer."), frappe.PermissionError)

	first_name, last_name = clean_name(first_name, _("First name")), clean_name(last_name, _("Last name"))
	phone = (phone or "").strip()
	if not PHONE_PATTERN.match(phone):
		frappe.throw(_("Please enter a valid phone number."))

	email = (email or "").strip().lower()
	if not validate_email_address(email):
		frappe.throw(_("Please enter a valid email address."))
	if frappe.db.exists("User", email):
		frappe.throw(_("An account with this email already exists. Try logging in instead."))

	try:
		user: User = frappe.get_doc(
			{
				"doctype": "User",
				"user_type": "Website User",
				"first_name": first_name,
				"last_name": last_name,
				"email": email,
				"phone": phone,
				"enabled": 1,
				"send_welcome_email": 1,
			}
		)
		user.insert(ignore_permissions=True)

		frappe.get_doc(
			{"doctype": "Client", "email": email, "phone_number": phone, "status": "Inactive"}
		).insert(ignore_permissions=True)
	except Exception:
		frappe.db.rollback()
		log_throw_error(_("Error creating user account. Please try again."))


def signup_allowed() -> bool:
	return bool(frappe.db.get_single_value("Zoezy Settings", "allow_client_signup"))


def clean_name(value: str | None, label: str) -> str:
	value = (value or "").strip()
	if not value or len(value) > MAX_NAME_LENGTH or re.search(r"[<>{}]", value):
		frappe.throw(_("Please enter a valid {0}.").format(label.lower()))
	return value
