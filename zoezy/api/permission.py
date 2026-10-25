import frappe

APP_ROLES = {"Client", "Trainer", "System Manager"}


def has_app_permission() -> bool:
	if frappe.session.user == "Administrator":
		return True
	return bool(APP_ROLES.intersection(frappe.get_roles()))
