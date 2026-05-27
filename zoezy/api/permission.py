import frappe


def has_app_permission():
    user = frappe.session.user
    if user == "Administrator":
        return True
    return False
