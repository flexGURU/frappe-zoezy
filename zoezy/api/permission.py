import frappe


def has_app_permission() -> bool:
    user = frappe.session.user
    if user == "Administrator":
        return True
    if "Client" in frappe.get_roles():
        return True

    return False
