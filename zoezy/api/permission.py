import frappe

APP_ROLES = {"Client", "Trainer", "System Manager"}
DESK_ROLES = {"Trainer", "System Manager"}


def has_app_permission() -> bool:
	if frappe.session.user == "Administrator":
		return True
	return bool(APP_ROLES.intersection(frappe.get_roles()))


def has_desk_permission() -> bool:
	if frappe.session.user == "Administrator":
		return True
	return bool(DESK_ROLES.intersection(frappe.get_roles()))


def has_portal_permission() -> bool:
	return "Client" in frappe.get_roles() and not has_desk_permission()
