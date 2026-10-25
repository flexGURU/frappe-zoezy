import frappe
from frappe.core.doctype.user.user import User

from zoezy.zoezy.doctype.zoezy_settings.zoezy_settings import get_settings

from .auth import PHONE_PATTERN, clean_name
from .utils import get_session_client


@frappe.whitelist()
def get_profile() -> dict:
	client_name = get_session_client()
	user: User = frappe.get_cached_doc("User", frappe.session.user)

	client = None
	if client_name:
		client = frappe.db.get_value(
			"Client",
			client_name,
			["status", "date_joined", "age"],
			as_dict=True,
		)

	return {
		"first_name": user.first_name,
		"last_name": user.last_name,
		"full_name": user.full_name,
		"email": user.email,
		"phone": user.phone,
		"image": user.user_image,
		"client": client,
		"settings": get_settings(),
	}


@frappe.whitelist(methods=["POST"])
def update_profile(first_name: str, last_name: str | None = None, phone: str | None = None) -> dict:
	get_session_client()

	first_name = clean_name(first_name, "First name")
	last_name = clean_name(last_name, "Last name") if (last_name or "").strip() else ""
	phone = (phone or "").strip()
	if phone and not PHONE_PATTERN.match(phone):
		frappe.throw("Please enter a valid phone number.")

	user: User = frappe.get_doc("User", frappe.session.user)
	user.first_name = first_name
	user.last_name = last_name
	user.phone = phone
	user.save(ignore_permissions=True)

	if client_name := get_session_client():
		client = frappe.get_doc("Client", client_name)
		client.phone_number = phone
		client.save(ignore_permissions=True)

	return get_profile()
